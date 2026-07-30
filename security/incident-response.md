# Incident Response Playbook

## Severity Levels

| Level | Description | Response Time | Escalation |
|-------|-------------|----------------|------------|
| **P0** | Critical - All users impacted | < 15 min | CEO + All hands |
| **P1** | Major - Many users impacted | < 1 hour | Eng Lead + Manager |
| **P2** | Moderate - Some users impacted | < 4 hours | On-call engineer |
| **P3** | Minor - Single user or edge case | < 1 business day | Standard queue |

## P0 Playbook: Complete Service Outage
1. PagerDuty alert fires
2. On-call engineer acknowledges
3. Status page updated to "investigating"
4. Escalate to incident commander
5. Review error logs & health endpoints
