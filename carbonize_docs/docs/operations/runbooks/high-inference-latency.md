# Runbook: High Inference Latency

## Alert
- **Name**: `InferenceLatencyHigh`
- **Severity**: P2
- **Trigger**: P95 inference latency > 500ms for 5 minutes

## Summary
ML inference latency has exceeded acceptable thresholds. This affects all real-time detection capabilities.

## Impact
- Detections may be delayed
- Robot decision-making is impacted
- WebSocket clients may experience timeouts

## Mitigation
1. **Scale horizontally**:
   ```bash
   kubectl scale deployment/inference --replicas=10 -n carbonize
   ```
2. **Restart inference workers**:
   ```bash
   kubectl rollout restart deployment/inference -n carbonize
   ```
