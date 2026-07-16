🔌 SHARED DATA SCHEMA — Sim ↔ Real Sensor Unification
Task 5.2: Design the DAQ → ingestion schema so real sensor data and simulated data share one schema
Owner: Hard-Tech Expert + Systems Designer
Priority: 🟠 High (avoid painful migration)
DoD: Shared Pydantic/JSON schema used by both sim-core output and planned real-sensor ingestion endpoint
Status: ✅ Complete

🎯 THE PROBLEM WE'RE PREVENTING
Without a shared schema:

Real sensor data: { timestamp, sensor_id, raw_value, unit }
Sim-core output:   { time, state_vector, derived }
                     ↑                ↑
                Different shapes!
When you try to validate your model against real data, you spend 3 months writing ETL code. Painful.

With a shared schema:

Both produce: { 
  metadata: { source, version, ... },
  timestamp: ISO-8601,
  measurements: [{ 
    sensor_id: "pH_main_loop",
    measurement_type: "pH",
    value: 7.2,
    unit: "pH",
    quality: "good" 
  }, ...] 
}
Validation dashboard consumes both. Done. ✅

🏛️ ARCHITECTURE OVERVIEW
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCTION SOURCES                                              │
│                                                                  │
│  ┌──────────────┐                  ┌──────────────┐              │
│  │   sim-core    │                  │  Real DAQ    │              │
│  │  (Cloud)     │                  │  (Plant)     │              │
│  │              │                  │              │              │
│  │  Emits       │                  │  Emits       │              │
│  │  Pydantic     │                  │  Pydantic     │              │
│  │  SimReading  │                  │  SensorReading│              │
│  └──────┬───────┘                  └──────┬───────┘              │
│         │                                │                      │
│         └──────────┬─────────────────────┘                      │
│                    │                                            │
│                    ▼                                            │
│         ┌──────────────────────────┐                          │
│         │   Ingestion API          │                          │
│         │   (POST /v1/ingest)      │                          │
│         └──────────┬───────────────┘                          │
│                    │                                            │
│                    ▼                                            │
│         ┌──────────────────────────┐                          │
│         │   Time-Series DB          │                          │
│         │   + Validation Dashboard  │                          │
│         └──────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘

🔄 SHARED USAGE EXAMPLES
From sim-core (Python)
# In sim-core: emit a synthetic reading
from cbms_shared.schemas.reading import (
    SensorReading, Measurement, BatchMetadata, DataSource
)
from datetime import datetime, timezone

reading = SensorReading(
    timestamp=datetime.now(timezone.utc),
    measurements=[
        Measurement(measurement_type="ph", value=8.5, unit="pH"),
        Measurement(measurement_type="temperature", value=40.0, unit="°C"),
        Measurement(measurement_type="co2_gas", value=0.8, unit="vol%"),
        Measurement(measurement_type="so2_gas", value=38.0, unit="ppm"),
        Measurement(measurement_type="turbidity", value=240.0, unit="NTU"),
    ],
    metadata=BatchMetadata(
        source=DataSource.SIMULATION,
        source_version="sim-core-0.3.1",
        plant_id=plant_uuid,
        simulation_id=sim_uuid,
    ),
)
From DAQ (C++ or Python edge)
# On the DAQ edge, after polling all sensors:
import httpx
from datetime import datetime, timezone
from cbms_shared.schemas.reading import (
    SensorReading, Measurement, BatchMetadata, DataSource
)

reading = SensorReading(
    timestamp=datetime.now(timezone.utc),
    measurements=[
        Measurement(measurement_type="ph", value=7.2, unit="pH", sensor_id="pH_main_loop"),
        Measurement(measurement_type="temperature", value=40.1, unit="°C", sensor_id="T_reactor"),
        Measurement(measurement_type="co2_gas", value=1.0, unit="vol%", sensor_id="CO2_analyzer"),
        Measurement(measurement_type="so2_gas", value=42.0, unit="ppm", sensor_id="SO2_analyzer"),
        Measurement(measurement_type="turbidity", value=280.0, unit="NTU", sensor_id="Turb_main"),
    ],
    metadata=BatchMetadata(
        source=DataSource.PHYSICAL_SENSOR,
        source_version="daq-fw-2.4.0",
        plant_id=plant_uuid,
    ),
)

response = httpx.post(
    f"{api_base}/api/v1/ingest",
    json=reading.model_dump(mode="json"),
    headers={"Authorization": f"Bearer {token}"},
)

From the dashboard (validation view)
// Frontend: visualize both real and simulated data on the same chart
interface ValidationViewProps {
  plantId: string;
  startTime: Date;
  endTime: Date;
}

function ValidationView({ plantId, startTime, endTime }: ValidationViewProps) {
  const { data: readings } = useQuery({
    queryKey: ["readings", plantId, startTime, endTime],
    queryFn: () => fetchReadings(plantId, startTime, endTime),
  });
  
  // Same chart works for both real and simulated data
  return (
    <Chart
      data={readings?.map(r => ({
        time: r.timestamp,
        real: r.get("co2_gas")?.value,        // From real DAQ
        simulated: r.get("co2_gas")?.metadata?.simulated_value, // From sim
      }))}
      series={["real", "simulated"]}
    />
  );
}

✅ TASK 5.2 COMPLETE
Deliverable: Shared Pydantic/JSON schema for sim-core and real sensor data
DoD met: Shared Pydantic/JSON schema used by both sim-core output and planned real-sensor ingestion endpoint
Key win: Zero migration pain. When the real pilot starts, data flows directly into the same schema that sim-core already uses.
