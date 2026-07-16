"""
Data ingestion and validation for the calibration pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator

from cbms_shared.exceptions import ValidationFailedError
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class DataValidationError(ValidationFailedError):
    """Raised when experimental data fails schema validation."""
    pass


class CE1DataSchema(BaseModel):
    """Schema for CE-1 (CA Kinetics) experimental data."""
    temperature_C: float = Field(..., ge=0, le=100, description="Temperature in Celsius")
    pH: float = Field(..., ge=0, le=14, description="Solution pH")
    CO2_mM: float = Field(..., ge=0, description="Dissolved CO2 concentration (mM)")
    rate_mol_per_L_s: float = Field(..., ge=0, description="CO2 hydration rate (mol/L/s)")
    CA_U_per_mL: float = Field(..., gt=0, description="CA activity (U/mL)")
    HCO3_mM: Optional[float] = Field(None, ge=0, description="Bicarbonate (mM)")
    time_h: Optional[float] = Field(None, ge=0, description="Time elapsed (h)")
    replicate: Optional[int] = Field(None, ge=1, description="Replicate number")
    
    @field_validator("rate_mol_per_L_s")
    @classmethod
    def check_rate_positive(cls, v):
        if v == 0:
            logger.warning("zero_rate_observed")
        return v


class CE2DataSchema(BaseModel):
    """Schema for CE-2 (Heavy Metal Sorption) experimental data."""
    metal: str = Field(..., pattern="^(Pb|Cd|Hg|As)$")
    pH: float = Field(..., ge=0, le=14)
    equilibrium_conc_mg_L: float = Field(..., ge=0, description="Ce (mg/L)")
    loading_mg_per_g: float = Field(..., ge=0, description="qe (mg/g)")
    chitosan_g_L: float = Field(..., gt=0, description="Chitosan dose (g/L)")
    temperature_C: Optional[float] = Field(None, ge=0, le=100)
    time_h: Optional[float] = Field(None, ge=0)
    replicate: Optional[int] = Field(None, ge=1)


class CE3DataSchema(BaseModel):
    """Schema for CE-3 (CaCO3 Precipitation) experimental data."""
    Ca_mM: float = Field(..., ge=0)
    HCO3_mM: float = Field(..., ge=0)
    pH: float = Field(..., ge=0, le=14)
    chitosan_pct: float = Field(..., ge=0, le=10)
    rate_mol_per_L_s: float = Field(..., ge=0)
    temperature_C: Optional[float] = Field(None, ge=0, le=100)
    time_h: Optional[float] = Field(None, ge=0)
    replicate: Optional[int] = Field(None, ge=1)


class CE4DataSchema(BaseModel):
    """Schema for CE-4 (Multi-Gas Absorption) experimental data."""
    timestamp: str
    gas: str = Field(..., pattern="^(CO2|SO2|NOx)$")
    inlet_ppm: float = Field(..., ge=0)
    outlet_ppm: float = Field(..., ge=0)
    pH: float = Field(..., ge=0, le=14)
    Ca_mM: float = Field(..., ge=0)
    temperature_C: Optional[float] = Field(None, ge=0, le=100)
    L_per_min: Optional[float] = Field(None, gt=0)
    replicate: Optional[int] = Field(None, ge=1)
    
    @field_validator("outlet_ppm")
    @classmethod
    def outlet_less_than_inlet(cls, v, info):
        inlet = info.data.get("inlet_ppm")
        if inlet is not None and v > inlet * 1.01:  # 1% tolerance
            raise ValueError(f"outlet ({v}) > inlet ({inlet}) — physically impossible")
        return v


class CE5DataSchema(BaseModel):
    """Schema for CE-5 (Formulation Screen) experimental data."""
    chitosan_pct: float = Field(..., ge=0, le=10)
    pH: float = Field(..., ge=0, le=14)
    response: float = Field(..., description="Measured response (units depend on design)")
    replicate: Optional[int] = Field(None, ge=1)


SCHEMAS = {
    "CE-1": CE1DataSchema,
    "CE-2": CE2DataSchema,
    "CE-3": CE3DataSchema,
    "CE-4": CE4DataSchema,
    "CE-5": CE5DataSchema,
}


class DataIngestor:
    """Load and validate experimental data."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def load_and_validate(
        self,
        data_path: Path,
        experiment: Optional[str] = None,
        schemas: Optional[Dict] = None,
    ) -> Tuple[pd.DataFrame, Optional[str]]:
        """
        Load CSV and validate against schema.
        """
        if not data_path.exists():
            raise DataValidationError(f"Data file not found: {data_path}")
        
        try:
            df = pd.read_csv(data_path, comment="#")
        except Exception as e:
            raise DataValidationError(f"Failed to parse CSV: {e}")
        
        if df.empty:
            raise DataValidationError("Data file is empty")
        
        if experiment is None or experiment is False:
            experiment = self._detect_experiment_type(df.columns, schemas)
            self.logger.info("experiment_auto_detected", experiment=experiment)
        
        if experiment not in SCHEMAS:
            raise DataValidationError(f"Unknown experiment type: {experiment}")
        
        schema_class = SCHEMAS[experiment]
        self._validate_dataframe(df, schema_class)
        
        # Convert numeric columns
        for field_name in schema_class.model_fields.keys():
            if field_name in df.columns and field_name != "metal" and field_name != "timestamp":
                df[field_name] = pd.to_numeric(df[field_name], errors="coerce")
        
        required_cols = [
            name for name, field in schema_class.model_fields.items()
            if field.is_required() and name in df.columns
        ]
        n_before = len(df)
        df = df.dropna(subset=required_cols)
        n_dropped = n_before - len(df)
        if n_dropped > 0:
            self.logger.warning("rows_dropped", count=n_dropped, reason="NaN in required columns")
        
        self._basic_stats_check(df, experiment)
        
        return df, experiment
    
    def _detect_experiment_type(
        self,
        columns: pd.Index,
        schemas: Dict,
    ) -> str:
        col_set = set(columns)
        scores = {}
        for exp_id, schema_info in schemas.items():
            required = set(schema_info["required_columns"])
            overlap = len(col_set & required) / len(required)
            scores[exp_id] = overlap
        
        best_match = max(scores, key=scores.get)
        if scores[best_match] < 0.8:
            raise DataValidationError(
                f"Could not auto-detect experiment type. Best match: {best_match} ({scores[best_match]:.0%}). "
                f"Specify --experiment explicitly."
            )
        return best_match
    
    def _validate_dataframe(
        self,
        df: pd.DataFrame,
        schema_class: type[BaseModel],
    ) -> None:
        required = [
            name for name, field in schema_class.model_fields.items()
            if field.is_required()
        ]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise DataValidationError(f"Missing required columns: {missing}")
        
        sample = df.head(100)
        errors = []
        for idx, row in sample.iterrows():
            try:
                schema_class(**row.to_dict())
            except Exception as e:
                errors.append(f"Row {idx}: {e}")
        
        if errors:
            self.logger.warning("row_validation_errors", count=len(errors), first_5=errors[:5])
    
    def _basic_stats_check(self, df: pd.DataFrame, experiment: str) -> None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if np.isinf(df[numeric_cols]).any().any():
            raise DataValidationError("Data contains infinite values")
        
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            if std > 0:
                outliers = ((df[col] - mean).abs() > 5 * std).sum()
                if outliers > 0:
                    self.logger.warning(
                        "potential_outliers",
                        column=col,
                        count=int(outliers),
                        mean=float(mean),
                        std=float(std),
                    )
