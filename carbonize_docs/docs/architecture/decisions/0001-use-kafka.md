# ADR-0001: Use Apache Kafka for Streaming Events

## Status
Accepted

## Date
2024-01-15

## Context
Carbonize needs to process high-throughput event streams from:
- Robot telemetry (~10k events/second)
- Detection results (~5k events/second)
- ML predictions (~1k events/second)

## Decision
We will use **Apache Kafka** as our core event streaming platform with Schema Registry and PyIceberg integration.

## Consequences
### Positive
- High throughput (>100k events/sec)
- Replay capabilities for ML model retraining
- Decouples producers and consumers
