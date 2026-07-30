# Carbonize Reference Architecture — Production Deployment

## Architecture Overview

```mermaid
graph TB
    subgraph "Edge Layer (Plant)"
        S1[Sensor 1: CO2, T, P, Flow]
        S2[Sensor 2: pH, Density, Viscosity]
        S3[Sensor 3: Emissions, Flue Gas]
        EDGE[Edge Gateway: MQTT/OPC-UA]
    end
    
    subgraph "Stream Processing"
        KAFKA[Apache Kafka: 3 brokers, 12 partitions]
        FLINK[Apache Flink: Windowed aggregation]
    end
    
    subgraph "ML/AI Layer"
        ML[ML Inference: Autoencoders, IsoForest]
        TRAIN[Model Training: PyTorch / Celery GPU]
        REGISTRY[MLflow Model Registry]
    end
    
    subgraph "Application Layer"
        API[FastAPI REST & WebSocket]
        WS[WebSocket Fan-out: 10k+ connections]
        AUTH[Auth Service: OAuth2 / JWT / RBAC]
    end
    
    subgraph "Storage Layer"
        PG[(PostgreSQL Primary & Replica)]
        TSDB[(InfluxDB / TimescaleDB)]
        S3[(S3/MinIO Object Storage)]
        REDIS[(Redis Cache & Queue)]
    end
    
    S1 --> EDGE
    S2 --> EDGE
    S3 --> EDGE
    EDGE --> KAFKA
    KAFKA --> FLINK
    FLINK --> ML
    FLINK --> TSDB
    ML --> WS
    API --> PG
    API --> REDIS
    WS --> API
    TRAIN --> REGISTRY
    REGISTRY --> ML
```

## Hardware Sizing Matrix

| Plant Size | Capacity | vCPUs | RAM | GPU | Storage | Network |
|---|---|---|---|---|---|---|
| Small | <100k t/yr | 8 | 32 GB | 1x T4 | 1 TB | 1 Gbps |
| Medium | 100k-1M t/yr | 32 | 128 GB | 4x A100 | 10 TB | 10 Gbps |
| Large | >1M t/yr | 128 | 512 GB | 16x A100 | 100 TB | 25 Gbps |

## Cloud Costs (Monthly)

| Tier | AWS | GCP | Azure |
|---|---|---|---|
| Small | $1,200 | $1,100 | $1,300 |
| Medium | $8,500 | $8,200 | $8,800 |
| Large | $42,000 | $40,000 | $44,000 |
