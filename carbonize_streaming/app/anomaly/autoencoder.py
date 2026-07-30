"""
PyTorch autoencoder for anomaly detection
"""
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, Tuple, Optional
from collections import deque
import logging
import time
import json
import pickle
from pathlib import Path


logger = logging.getLogger(__name__)


class LSTMAutoencoder(nn.Module):
    """LSTM-based autoencoder for time-series anomaly detection."""
    
    def __init__(self, input_dim: int = 1, hidden_dim: int = 64, 
                 num_layers: int = 2, sequence_length: int = 60):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.sequence_length = sequence_length
        
        self.encoder = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0,
        )
        
        self.bottleneck = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, hidden_dim),
        )
        
        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0,
        )
        
        self.output_layer = nn.Linear(hidden_dim, input_dim)
    
    def forward(self, x):
        encoded, (hidden, cell) = self.encoder(x)
        last_hidden = hidden[-1]
        bottleneck = self.bottleneck(last_hidden)
        decoder_input = bottleneck.unsqueeze(1).repeat(1, x.size(1), 1)
        decoded, _ = self.decoder(decoder_input)
        output = self.output_layer(decoded)
        return output


class TransformerAutoencoder(nn.Module):
    """Transformer-based autoencoder for better sequence learning."""
    
    def __init__(self, input_dim: int = 1, d_model: int = 64, 
                 nhead: int = 4, num_layers: int = 3, 
                 sequence_length: int = 60):
        super().__init__()
        
        self.input_projection = nn.Linear(input_dim, d_model)
        self.positional_encoding = nn.Parameter(
            torch.randn(1, sequence_length, d_model) * 0.02
        )
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first=True,
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        
        self.output_projection = nn.Linear(d_model, input_dim)
    
    def forward(self, x):
        x_proj = self.input_projection(x) + self.positional_encoding
        encoded = self.encoder(x_proj)
        decoded = self.decoder(x_proj, encoded)
        return self.output_projection(decoded)


class VariationalAutoencoder(nn.Module):
    """Variational autoencoder for probabilistic anomaly detection."""
    
    def __init__(self, input_dim: int = 1, hidden_dim: int = 64, latent_dim: int = 16):
        super().__init__()
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, hidden_dim),
            nn.ReLU(),
        )
        
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)
        
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim),
        )
    
    def encode(self, x):
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_logvar(h)
    
    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar


class StreamingAutoencoderDetector:
    """Production streaming autoencoder detector."""
    
    def __init__(
        self,
        feature_dim: int = 1,
        sequence_length: int = 60,
        hidden_dim: int = 64,
        model_type: str = 'lstm',
        learning_rate: float = 1e-3,
        device: str = 'cpu',
        window_size: int = 1000,
        threshold_percentile: float = 95.0,
        retrain_interval: int = 1000,
    ):
        self.feature_dim = feature_dim
        self.sequence_length = sequence_length
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.threshold_percentile = threshold_percentile
        self.retrain_interval = retrain_interval
        self._samples_since_train = 0
        
        self.model_type = model_type
        if model_type == 'lstm':
            self.model = LSTMAutoencoder(
                input_dim=feature_dim,
                hidden_dim=hidden_dim,
                sequence_length=sequence_length,
            ).to(self.device)
        elif model_type == 'transformer':
            self.model = TransformerAutoencoder(
                input_dim=feature_dim,
                d_model=hidden_dim,
                sequence_length=sequence_length,
            ).to(self.device)
        elif model_type == 'vae':
            self.model = VariationalAutoencoder(
                input_dim=feature_dim,
                hidden_dim=hidden_dim,
            ).to(self.device)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        self._buffer = deque(maxlen=window_size)
        self._training_buffer = deque(maxlen=window_size)
        self._error_history = deque(maxlen=window_size)
        self._threshold = None
        self._is_trained = False
    
    def add_value(self, value: float) -> Optional[Dict]:
        """Add a value and get anomaly score."""
        self._buffer.append(float(value))
        self._training_buffer.append(float(value))
        self._samples_since_train += 1
        
        if len(self._buffer) < self.sequence_length:
            return None
        
        score = self._compute_reconstruction_error()
        self._error_history.append(score)
        
        self._update_threshold()
        is_anomaly = self._threshold is not None and score > self._threshold
        
        return {
            'value': float(value),
            'score': float(score),
            'threshold': float(self._threshold) if self._threshold else 0.0,
            'is_anomaly': bool(is_anomaly),
            'severity': self._get_severity(score),
            'timestamp': int(time.time() * 1000),
        }
    
    def _compute_reconstruction_error(self) -> float:
        """Compute reconstruction error for current sequence."""
        recent = list(self._buffer)[-self.sequence_length:]
        sequence = torch.FloatTensor(recent).unsqueeze(0).unsqueeze(-1).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            if self.model_type == 'vae':
                reconstructed, mu, logvar = self.model(sequence)
            else:
                reconstructed = self.model(sequence)
        
        error = self.criterion(reconstructed, sequence).item()
        return error
    
    def _update_threshold(self):
        """Update anomaly threshold based on error history."""
        if len(self._error_history) < 10:
            self._threshold = 0.5
            return
        errors = list(self._error_history)
        self._threshold = float(np.percentile(errors, self.threshold_percentile))
    
    def _get_severity(self, score: float) -> str:
        """Determine severity based on score ratio."""
        if self._threshold is None or self._threshold == 0:
            return 'medium'
        ratio = score / self._threshold
        if ratio > 3.0:
            return 'critical'
        elif ratio > 2.0:
            return 'high'
        elif ratio > 1.5:
            return 'medium'
        else:
            return 'low'
