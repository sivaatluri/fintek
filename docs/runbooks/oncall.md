# On-Call Runbook

## Overview

This runbook provides guidance for on-call engineers supporting the FinOps SaaS platform. It covers common incidents, troubleshooting steps, and escalation procedures.

## On-Call Responsibilities

- Respond to critical alerts within 15 minutes
- Investigate and resolve incidents
- Communicate status to stakeholders
- Document incidents in post-mortems
- Handoff context during shift changes

## Alert Severity Levels

### P0 - Critical (Response: Immediate)
- Platform completely unavailable
- Data corruption or loss
- Security breach
- Revenue-impacting outage

**Actions**:
- Acknowledge immediately
- Page backup on-call if needed
- Start incident bridge
- Update status page
- Notify leadership

### P1 - High (Response: 15 minutes)
- Degraded performance affecting users
- Service partially unavailable
- Data ingestion delays (>4 hours)
- Critical feature broken

**Actions**:
- Acknowledge within 15 min
- Investigate and diagnose
- Update stakeholders hourly
- Prepare rollback if needed

### P2 - Medium (Response: 1 hour)
- Minor feature degradation
- Non-critical service issues
- Query performance problems
- Alert fatigue / false positives

**Actions**:
- Acknowledge within 1 hour
- Investigate during business hours
- Create ticket for follow-up
- Fix in next deployment

### P3 - Low (Response: Next business day)
- Cosmetic issues
- Documentation problems
- Enhancement requests
- Non-urgent maintenance

## Common Incidents

### 1. Platform Unavailable

**Symptoms**:
- Users cannot access web UI
- API returns 502/503 errors
- Health checks failing

**Investigation**:
```bash
# Check service health
kubectl get pods -n finops
kubectl describe pod <pod-name> -n finops

# Check recent deployments
kubectl rollout history deployment/gateway-api -n finops

# Check logs
kubectl logs -n finops deployment/gateway-api --tail=100

# Check database connectivity
kubectl exec -it <pod> -n finops -- psql $DATABASE_URL -c "SELECT 1"
```

**Common Causes**:
- Recent deployment issue → Rollback
- Database connection exhaustion → Scale up connection pool
- Memory/CPU limits → Scale horizontally
- External dependency down → Check integrations

**Resolution**:
```bash
# Rollback deployment
kubectl rollout undo deployment/gateway-api -n finops

# Scale up if resource constrained
kubectl scale deployment/gateway-api --replicas=5 -n finops

# Restart if stuck
kubectl rollout restart deployment/gateway-api -n finops
```

### 2. Cost Data Not Updating

**Symptoms**:
- Cost data stale (>24 hours old)
- Dashboards showing old data
- Ingestion jobs failing

**Investigation**:
```bash
# Check ingestion service
kubectl logs -n finops deployment/cost-ingestion-service --tail=100

# Check Kafka topics
kafka-console-consumer --bootstrap-server kafka:9092 \
  --topic cost-ingestion-events --from-beginning --max-messages 10

# Check data lake
aws s3 ls s3://finops-data/tenant_id=<tenant>/provider=aws/ \
  --recursive | tail -20

# Check connector status
curl http://cost-ingestion-service:8080/api/connectors/status
```

**Common Causes**:
- Cloud provider API credentials expired → Rotate credentials
- S3/storage permission issues → Check IAM policies
- Connector crash/restart loop → Check connector logs
- Data format changed → Update parser

**Resolution**:
```bash
# Manually trigger ingestion
curl -X POST http://cost-ingestion-service:8080/api/ingestion/trigger \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"<tenant>","provider":"aws","start_date":"2026-02-09"}'

# Restart connector
kubectl rollout restart deployment/aws-cur-connector -n finops

# Check credentials
kubectl get secret aws-credentials -n finops -o yaml
```

### 3. Query Performance Degraded

**Symptoms**:
- Dashboard load time >30 seconds
- API timeouts
- Query engine CPU at 100%

**Investigation**:
```sql
-- Check long-running queries (Postgres)
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '30 seconds'
ORDER BY duration DESC;

-- Check Trino queries
curl http://trino:8080/v1/query | jq '.[] | select(.state=="RUNNING")'
```

**Common Causes**:
- Missing partition filters → Add where clause
- Query scanning too much data → Add partition pruning
- Missing indexes → Add indexes
- Resource limits → Scale query engine

**Resolution**:
```bash
# Scale query engine
kubectl scale deployment/trino-worker --replicas=5 -n finops

# Kill problematic query
SELECT pg_terminate_backend(<pid>);

# Add query timeout
ALTER DATABASE finops SET statement_timeout = '60s';

# Cache frequently accessed data
# (configure in Redis)
```

### 4. Budget Alerts Not Firing

**Symptoms**:
- Users report missing alerts
- No Slack notifications
- Budget exceeded but no alert

**Investigation**:
```bash
# Check budgets-alerts-service
kubectl logs -n finops deployment/budgets-alerts-service --tail=100

# Check workflow engine
kubectl logs -n finops deployment/workflows-service --tail=100

# Check Kafka events
kafka-console-consumer --bootstrap-server kafka:9092 \
  --topic budget-events --from-beginning --max-messages 10

# Check database budget records
psql $DATABASE_URL -c "SELECT * FROM budgets WHERE id='<budget-id>'"
```

**Common Causes**:
- Workflow service down → Restart service
- Kafka consumer lag → Check consumer group
- Budget threshold misconfigured → Verify budget settings
- Integration service issues → Check Slack/email service

**Resolution**:
```bash
# Restart workflow service
kubectl rollout restart deployment/workflows-service -n finops

# Check consumer lag
kafka-consumer-groups --bootstrap-server kafka:9092 \
  --group workflows-consumer --describe

# Manually trigger workflow
curl -X POST http://workflows-service:8080/api/workflows/trigger \
  -H "Content-Type: application/json" \
  -d '{"workflow_id":"<id>","event":{"type":"budget.threshold_exceeded"}}'
```

### 5. Authentication Failures

**Symptoms**:
- Users cannot log in
- SSO redirect fails
- Token validation errors

**Investigation**:
```bash
# Check auth service
kubectl logs -n finops deployment/auth-service --tail=100

# Check SSO provider connectivity
curl -v https://sso-provider.example.com/.well-known/openid-configuration

# Check Redis (session store)
redis-cli ping
redis-cli keys "session:*" | wc -l

# Check JWT validation
curl -H "Authorization: Bearer <token>" \
  http://gateway-api:3000/api/user/me
```

**Common Causes**:
- SSO provider down → Check status page
- Redis down → Restart Redis
- Certificate expired → Renew certificate
- Session timeout → Adjust timeout settings

**Resolution**:
```bash
# Restart auth service
kubectl rollout restart deployment/auth-service -n finops

# Clear Redis sessions if needed
redis-cli FLUSHDB

# Update SSO configuration
kubectl edit configmap auth-config -n finops
```

## Service Dependencies

```
┌──────────────┐
│   Web UI     │
└──────┬───────┘
       │
┌──────▼───────┐
│  Gateway API │──────┐
└──────┬───────┘      │
       │              │
       ├──────────────┼──────────────────┐
       │              │                  │
┌──────▼───────┐ ┌───▼────────┐  ┌─────▼─────┐
│ Auth Service │ │   Tenant   │  │  Budgets  │
└──────┬───────┘ │  Service   │  │  Service  │
       │         └───┬────────┘  └─────┬─────┘
       │             │                 │
┌──────▼─────────────▼─────────────────▼─────┐
│           PostgreSQL Database              │
└────────────────────────────────────────────┘

┌──────▼─────────────▼─────────────────▼─────┐
│              Redis Cache                    │
└─────────────────────────────────────────────┘
```

## Escalation Procedures

### Level 1: On-Call Engineer (You)
- Initial response and triage
- Standard troubleshooting
- Document findings

### Level 2: Senior Engineer
- Escalate if incident persists >1 hour
- Complex issues requiring deep expertise
- Architecture decisions needed

### Level 3: Platform Lead
- Critical incidents (P0)
- Multiple service failures
- Strategic decisions required

### Level 4: Leadership
- Extended outages (>4 hours)
- Data breach or security incident
- Customer escalations

## Communication Templates

### Incident Start
```
🚨 INCIDENT ALERT
Severity: [P0/P1/P2/P3]
Started: [timestamp]
Impact: [description]
Status: Investigating

We are aware of [issue] affecting [component].
Team is investigating. Updates every [frequency].
```

### Incident Update
```
📊 INCIDENT UPDATE [#N]
Updated: [timestamp]
Status: [Investigating/Identified/Monitoring/Resolved]

Current situation: [details]
Actions taken: [list]
Next steps: [list]

ETA: [if known]
Next update: [time]
```

### Incident Resolution
```
✅ INCIDENT RESOLVED
Resolved: [timestamp]
Duration: [time]
Root cause: [brief description]

Resolution: [what was done]
Impact: [who was affected]
Follow-up: [ticket link]

Post-mortem: [date of review]
```

## Useful Commands

### Kubernetes
```bash
# Get all pods status
kubectl get pods -n finops

# Get pod logs
kubectl logs -n finops <pod-name> --tail=100 -f

# Describe pod
kubectl describe pod <pod-name> -n finops

# Execute command in pod
kubectl exec -it <pod-name> -n finops -- /bin/sh

# Port forward for local debugging
kubectl port-forward -n finops svc/gateway-api 3000:3000

# Scale deployment
kubectl scale deployment/<name> --replicas=3 -n finops

# Rollback deployment
kubectl rollout undo deployment/<name> -n finops

# View deployment history
kubectl rollout history deployment/<name> -n finops
```

### Database
```bash
# Connect to database
psql $DATABASE_URL

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC LIMIT 10;

# Database size
SELECT pg_size_pretty(pg_database_size('finops_db'));
```

### Redis
```bash
# Check Redis health
redis-cli ping

# Get info
redis-cli info

# Check memory usage
redis-cli info memory

# Clear cache
redis-cli FLUSHDB
```

### Logs
```bash
# Search logs (if using ELK/Loki)
# Example with kubectl logs
kubectl logs -n finops -l app=gateway-api --tail=1000 | grep ERROR

# Follow logs
kubectl logs -n finops -l app=gateway-api -f

# Logs from specific time
kubectl logs -n finops <pod> --since=1h
```

## Health Checks

### Service Health Endpoints
- Gateway API: `http://gateway-api:3000/health`
- Auth Service: `http://auth-service:8080/health`
- Cost Ingestion: `http://cost-ingestion:8080/health`
- Workflows: `http://workflows-service:8080/health`

### Quick Health Check Script
```bash
#!/bin/bash
services=(
  "gateway-api:3000"
  "auth-service:8080"
  "cost-ingestion:8080"
  "workflows-service:8080"
)

for service in "${services[@]}"; do
  if curl -f "http://$service/health" > /dev/null 2>&1; then
    echo "✓ $service"
  else
    echo "✗ $service UNHEALTHY"
  fi
done
```

## Post-Incident Actions

1. **Incident Report**: Document in incident tracking system
2. **Communication**: Notify affected users
3. **Post-Mortem**: Schedule within 48 hours
4. **Action Items**: Create tickets for improvements
5. **Runbook Update**: Add learnings to this document

## Contact Information

- **On-Call Schedule**: PagerDuty rotation
- **Slack Channel**: #finops-oncall
- **War Room**: Zoom link in PagerDuty alert
- **Status Page**: https://status.finops.example.com

## Additional Resources

- [Incident Response](./incident_response.md)
- [Data Quality Runbook](./data_quality.md)
- [Backup & Restore](./backups_restore.md)
- [Architecture Docs](/docs/architecture/)
