# Deployment Checklist

## Before merge to main
- [ ] All CI checks pass (lint, types, tests, security)
- [ ] At least 1 reviewer approved
- [ ] No "do not merge" labels
- [ ] Database migrations included (if any)
- [ ] CHANGELOG.md updated

## Auto-deploy to staging
- Happens automatically on merge to main
- Watch Slack #deploys channel
- Smoke tests run automatically

## Promote to production
- Go to Actions tab → "Deploy to Production" → Run workflow
- Choose branch: main
- Monitor canary metrics (5 min)
- If errors > threshold, auto-rollback
