"""
Generate Mermaid diagrams from architecture specs
"""
from pathlib import Path


class DiagramGenerator:
    """Generate Mermaid diagrams and architecture documentation."""
    
    def __init__(self, output_dir: str = 'docs/architecture/diagrams'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_data_flow_diagram(self) -> Path:
        """Generate data flow diagram."""
        path = self.output_dir / "data-flow.md"
        content = """# Data Flow Diagrams

```mermaid
sequenceDiagram
    participant Robot
    participant ROS2
    participant Kafka
    participant Flink
    participant ML
    participant DB
    participant API
    participant Dashboard

    Robot->>ROS2: Sensor data
    ROS2->>Kafka: Publish telemetry
    Kafka->>Flink: Stream events
    par Stream Processing
        Flink->>ML: Anomaly detection
        ML-->>Flink: Anomaly score
        Flink->>DB: Aggregated metrics
    end
    Flink->>Kafka: Enriched events
    Kafka->>API: WebSocket push
    API->>Dashboard: Real-time update
```
"""
        path.write_text(content)
        return path
    
    def generate_deployment_diagram(self) -> Path:
        """Generate K8s deployment diagram."""
        path = self.output_dir / "deployment.md"
        content = """# Kubernetes Deployment Topology

```mermaid
graph TB
    subgraph "Production Cluster"
        ING[Ingress Controller]
        DASH[Dashboard]
        API[FastAPI x4]
        INF1[GPU Worker 1]
        FLINK[Flink JobManager]
        PG[(PostgreSQL)]
        K1[Kafka Broker]
    end
    ING --> DASH
    ING --> API
    API --> PG
    API --> K1
    K1 --> FLINK
```
"""
        path.write_text(content)
        return path


if __name__ == '__main__':
    gen = DiagramGenerator()
    gen.generate_data_flow_diagram()
    gen.generate_deployment_diagram()
