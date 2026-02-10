# FinOps Analyst Persona

## Overview

The FinOps Analyst is a practitioner responsible for day-to-day cost management, optimization, and reporting. They are the primary users of the platform and bridge the gap between finance and engineering.

## Key Responsibilities

- Daily cost monitoring and analysis
- Budget management and forecasting
- Cost allocation and chargeback
- Optimization recommendations
- Anomaly investigation
- Reporting and communication
- Policy enforcement
- Vendor management

## Dashboard Views

### FinOps Overview Dashboard

**Key Metrics**
- Daily spend and trends
- Active budget status (all budgets)
- Open recommendations
- Pending anomaly investigations
- Allocation coverage %
- Tag compliance rate

**Quick Actions**
- Create budget
- Investigate anomaly
- Review recommendation
- Export report
- Configure alert

### Cost Analysis

**Detailed Breakdowns**
- By provider (AWS, Azure, GCP)
- By service (compute, storage, database)
- By account/subscription
- By tag (environment, team, project)
- By commitment type (on-demand, RI, SP)

**Time Ranges**
- Today, Yesterday, Week, Month, Quarter, Year
- Custom date ranges
- Comparison periods (WoW, MoM, YoY)

### Budget Management

**Budget Views**
- All budgets (list and cards)
- Budget vs. actual charts
- Forecast vs. budget
- Historical performance
- Variance analysis

**Budget Actions**
- Create/edit/delete budgets
- Configure alerts and thresholds
- Set up approval workflows
- Add notes and context

### Recommendations

**Optimization Categories**
- Reserved Instances / Savings Plans
- Rightsizing opportunities
- Idle resource cleanup
- Storage optimization
- Commitment coverage gaps

**Recommendation Details**
- Estimated monthly savings
- Implementation effort
- Confidence score
- Historical usage patterns
- Step-by-step implementation guide

### Allocation Engine

**Allocation Methods**
- Direct tagging
- Proportional allocation
- Fixed allocation
- Rule-based allocation
- Shared cost allocation

**Unit Economics**
- Cost per user
- Cost per transaction
- Cost per feature
- Custom business metrics

## Use Cases

### 1. Daily Cost Review

**Time**: 30 minutes every morning

**Workflow**:
1. Check overnight alerts
2. Review yesterday's spend vs. forecast
3. Investigate any anomalies
4. Check budget status for current month
5. Review new recommendations
6. Update stakeholders on significant findings

### 2. Monthly Budget Close

**Time**: End of month

**Workflow**:
1. Run final month-end reports
2. Compare actual vs. budget for all teams
3. Document variances and reasons
4. Update forecasts for remaining year
5. Create executive summary
6. Present findings to stakeholders
7. Update budgets for next month

### 3. Cost Optimization Sprint

**Time**: 2-4 hours weekly

**Workflow**:
1. Review all open recommendations
2. Prioritize by savings potential and effort
3. Validate recommendations with usage data
4. Coordinate with engineering teams
5. Track implementation progress
6. Measure realized savings
7. Document lessons learned

### 4. Chargeback Report Generation

**Time**: Weekly or monthly

**Workflow**:
1. Verify allocation rules are current
2. Review tag compliance
3. Run allocation calculations
4. Generate chargeback reports per team
5. Validate with team leads
6. Publish to finance system
7. Address questions and disputes

### 5. Anomaly Investigation

**Triggered by alert**

**Workflow**:
1. Review anomaly details (service, magnitude, time)
2. Check for recent deployments or changes
3. Analyze usage patterns
4. Identify root cause
5. Assign to responsible team if external
6. Document findings
7. Create Jira ticket if action needed
8. Set up alert to prevent recurrence

## Required Permissions

### Full Access
- All dashboards and analytics
- Budget creation and management
- Recommendation review and implementation
- Allocation rule configuration
- Report generation and scheduling
- Tag management
- Virtual tagging rules

### Limited Access
- User management (view only)
- Integration configuration (with approval)
- Workflow creation (with approval)

### No Access
- Infrastructure changes
- SSO/SAML configuration
- Billing account changes

## Tools & Features

### Cost Explorer
- Multi-dimensional analysis
- Custom grouping and filtering
- Saved queries and views
- Export to CSV/Excel
- Sharing and collaboration

### Budget Builder
- Templates for common budget types
- Hierarchical budgets (parent/child)
- Multiple threshold alerts
- Slack/email integration
- Approval workflows

### Recommendation Engine
- Automated daily scans
- Customizable detection rules
- Savings calculators
- Implementation tracking
- ROI measurement

### Allocation Engine
- Drag-and-drop rule builder
- Tag propagation
- Shared cost distribution
- Unit cost calculation
- What-if modeling

### Reporting Suite
- Pre-built report templates
- Custom report builder
- Scheduled delivery
- Multi-format export
- Recipient management

### Tagging Tools
- Tag compliance dashboard
- Missing tag identification
- Virtual tag rules
- Bulk tag operations
- Tag governance policies

## Best Practices

### 1. Establish Routines

**Daily (30 min)**
- Review overnight costs
- Check active alerts
- Quick anomaly scan
- Respond to urgent requests

**Weekly (2 hours)**
- Deep dive into trends
- Review new recommendations
- Update stakeholders
- Optimization sprint planning

**Monthly (4-6 hours)**
- Budget close and reconciliation
- Generate executive reports
- Forecast review and update
- Strategic planning with teams

### 2. Proactive Monitoring

- Set meaningful alert thresholds
- Monitor forecast accuracy
- Track budget burn rates
- Watch for usage pattern changes
- Stay ahead of potential issues

### 3. Communication

**Stakeholder Updates**
- Weekly email summaries
- Monthly team meetings
- Quarterly business reviews
- Ad-hoc issue notifications

**Documentation**
- Document all investigations
- Keep runbooks updated
- Share optimization wins
- Build knowledge base

### 4. Collaboration

**With Engineering**
- Attend sprint planning
- Review architecture changes
- Provide cost feedback
- Support optimization efforts

**With Finance**
- Reconcile invoices
- Explain variances
- Support budget planning
- Align on reporting

**With Leadership**
- Provide strategic insights
- Support decision-making
- Report on savings
- Propose initiatives

## Advanced Features

### Custom Dashboards
Create personalized dashboards with:
- Favorite metrics
- Team-specific views
- Custom date ranges
- Saved filters

### API Access
Automate tasks using REST API:
- Export cost data
- Update budgets
- Trigger reports
- Manage tags

### Workflow Automation
Create custom workflows:
- Auto-tag resources
- Alert on patterns
- Create tickets
- Send notifications

## Key Metrics to Track

### Cost Metrics
- Daily/weekly/monthly spend
- Cost per business unit
- Cost per product/service
- Unit economics
- Waste percentage

### Efficiency Metrics
- RI/SP coverage
- RI/SP utilization
- Rightsizing opportunities addressed
- Tag compliance rate
- Allocation coverage

### Performance Metrics
- Budget adherence
- Forecast accuracy
- Time to detect anomalies
- Time to implement recommendations
- Realized savings

## Common Scenarios

### Scenario 1: Sudden Cost Spike
*"AWS spend increased 40% yesterday. What happened?"*

**Investigation**:
1. Filter to AWS, yesterday
2. Group by service to find spike
3. Drill into service details
4. Check resource IDs and tags
5. Correlate with deployment events
6. Contact responsible team
7. Create action plan

### Scenario 2: Budget Running Out
*"Engineering team is at 85% of monthly budget with 10 days left."*

**Response**:
1. Analyze daily burn rate
2. Forecast end-of-month spend
3. Review upcoming commitments
4. Identify quick wins for savings
5. Meet with engineering lead
6. Adjust forecast or budget
7. Increase monitoring frequency

### Scenario 3: Low RI Coverage
*"Compute RI coverage is only 30%. How do we improve it?"*

**Action Plan**:
1. Analyze stable workload usage
2. Generate RI recommendations
3. Calculate savings potential
4. Review with engineering and finance
5. Submit RI purchase proposal
6. Track implementation
7. Measure realized savings

## Getting Started

### Week 1: Learning
- Complete platform training
- Review existing budgets and alerts
- Understand current allocation model
- Meet key stakeholders
- Shadow senior analyst

### Week 2: Setup
- Configure personal dashboard
- Set up alert preferences
- Create saved views
- Schedule recurring reports
- Document processes

### Month 1: Active Management
- Take ownership of budgets
- Start daily review routine
- Implement first optimizations
- Build stakeholder relationships
- Establish communication cadence

### Ongoing: Improvement
- Refine processes
- Automate repetitive tasks
- Share best practices
- Stay current with cloud pricing
- Contribute to knowledge base

## Resources

- **Training**: Internal FinOps certification program
- **Community**: Monthly FinOps practitioner meetup
- **Documentation**: Complete platform documentation
- **Support**: Dedicated Slack channel #finops-help
- **External**: FinOps Foundation resources

## Success Criteria

### First 30 Days
- ✓ Complete platform training
- ✓ Own budget monitoring
- ✓ Identify first optimization
- ✓ Build stakeholder rapport

### First 90 Days
- ✓ Establish review routines
- ✓ Implement 5+ optimizations
- ✓ Generate first chargeback report
- ✓ Achieve >90% budget accuracy

### First Year
- ✓ Drive 15%+ in savings
- ✓ Improve tag compliance to >85%
- ✓ Automate 50%+ of tasks
- ✓ Become trusted advisor to teams
