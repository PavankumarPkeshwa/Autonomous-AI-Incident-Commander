# AWS Deployment Quick Start Guide

This file provides the fastest path to deploying your application to AWS.

## 5-Minute Quick Setup (Using CloudFormation)

### Step 1: Set Environment Variables (PowerShell)
```powershell
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$ENVIRONMENT = "staging"  # or "production"
$STACK_NAME = "incident-commander-$ENVIRONMENT"
```

### Step 2: Create Secrets Manager Entry
```powershell
aws secretsmanager create-secret `
  --name incident-commander/groq-key `
  --secret-string '{"GROQ_API_KEY":"your-groq-api-key-here"}' `
  --region $AWS_REGION
```

### Step 3: Deploy Infrastructure with CloudFormation
```powershell
# Create S3 bucket for CloudFormation
$CF_BUCKET = "cf-templates-$AWS_ACCOUNT_ID-$AWS_REGION"
aws s3api create-bucket --bucket $CF_BUCKET --region $AWS_REGION 2>$null

# Upload template
aws s3 cp cloudformation-template.yaml s3://$CF_BUCKET/

# Create stack
aws cloudformation create-stack `
  --stack-name $STACK_NAME `
  --template-url "https://s3.amazonaws.com/$CF_BUCKET/cloudformation-template.yaml" `
  --parameters `
    ParameterKey=Environment,ParameterValue=$ENVIRONMENT `
    ParameterKey=DesiredCount,ParameterValue=2 `
  --capabilities CAPABILITY_IAM `
  --region $AWS_REGION

# Monitor stack creation
aws cloudformation describe-stacks `
  --stack-name $STACK_NAME `
  --query 'Stacks[0].StackStatus' `
  --region $AWS_REGION
```

### Step 4: Build and Push Docker Image
```powershell
# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login `
  --username AWS `
  --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build image
docker build -f Dockerfile -t incident-commander-backend:latest .

# Tag for ECR
$ECR_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/incident-commander-backend"
docker tag incident-commander-backend:latest "${ECR_URI}:latest"

# Push to ECR
docker push "${ECR_URI}:latest"
```

### Step 5: Build and Deploy Frontend
```powershell
# Build frontend
cd ui
npm install
npm run build
cd ..

# Create S3 bucket for frontend
$S3_BUCKET = "incident-commander-frontend-$ENVIRONMENT"
aws s3api create-bucket --bucket $S3_BUCKET --region $AWS_REGION

# Upload to S3
aws s3 sync ui/dist/ s3://$S3_BUCKET/ --delete

# Get ALB DNS name from CloudFormation
$ALB_DNS = aws cloudformation describe-stacks `
  --stack-name $STACK_NAME `
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' `
  --output text `
  --region $AWS_REGION

Write-Host "Frontend: http://$ALB_DNS"
Write-Host "API Docs: http://$ALB_DNS/docs"
```

---

## Manual Step-by-Step (If CloudFormation Doesn't Work)

### 1. Create ECR Repository
```powershell
aws ecr create-repository `
  --repository-name incident-commander-backend `
  --region $AWS_REGION
```

### 2. Build and Push Docker Image
```powershell
docker build -f Dockerfile -t incident-commander-backend:latest .
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
docker tag incident-commander-backend:latest "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/incident-commander-backend:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/incident-commander-backend:latest"
```

### 3. Create ECS Cluster
```powershell
aws ecs create-cluster --cluster-name incident-commander --region $AWS_REGION
aws logs create-log-group --log-group-name /ecs/incident-commander --region $AWS_REGION
```

### 4. Register Task Definition
```powershell
aws ecs register-task-definition `
  --family incident-commander-backend `
  --network-mode awsvpc `
  --requires-compatibilities FARGATE `
  --cpu 256 `
  --memory 512 `
  --container-definitions @"
[
  {
    "name": "incident-commander",
    "image": "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/incident-commander-backend:latest",
    "portMappings": [
      {
        "containerPort": 8000,
        "hostPort": 8000,
        "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/incident-commander",
        "awslogs-region": "$AWS_REGION",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "environment": [
      {"name": "API_HOST", "value": "0.0.0.0"},
      {"name": "API_PORT", "value": "8000"}
    ],
    "secrets": [
      {
        "name": "GROQ_API_KEY",
        "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$AWS_ACCOUNT_ID:secret:incident-commander/groq-key:GROQ_API_KEY::"
      }
    ]
  }
]
"@ `
  --execution-role-arn "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole" `
  --region $AWS_REGION
```

### 5. Create Application Load Balancer
```powershell
# Get default VPC and subnets
$VPC_ID = aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION
$SUBNETS = aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[0:2].SubnetId' --output text --region $AWS_REGION

# Create ALB
$ALB = aws elbv2 create-load-balancer `
  --name incident-commander-alb `
  --subnets $SUBNETS.Split() `
  --scheme internet-facing `
  --type application `
  --region $AWS_REGION `
  --query 'LoadBalancers[0].LoadBalancerArn' `
  --output text

# Create target group
aws elbv2 create-target-group `
  --name incident-commander-tg `
  --protocol HTTP `
  --port 8000 `
  --vpc-id $VPC_ID `
  --target-type ip `
  --health-check-path /docs `
  --region $AWS_REGION
```

### 6. Create ECS Service
```powershell
# Get security group ID
$SG_ID = aws ec2 create-security-group `
  --group-name incident-commander-sg `
  --description "ECS security group" `
  --vpc-id $VPC_ID `
  --query 'GroupId' `
  --output text `
  --region $AWS_REGION

# Allow traffic
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 8000 `
  --cidr 0.0.0.0/0 `
  --region $AWS_REGION

# Create service
aws ecs create-service `
  --cluster incident-commander `
  --service-name incident-commander-api `
  --task-definition incident-commander-backend:1 `
  --desired-count 2 `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
  --region $AWS_REGION
```

---

## Deployment Using the Automation Script

```powershell
# Make script executable
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run full deployment
.\deploy.ps1 -Action full-deployment -Environment staging -Region us-east-1

# Check status
.\deploy.ps1 -Action check-health

# View logs
.\deploy.ps1 -Action view-logs
```

---

## Post-Deployment Steps

### 1. Get ALB DNS Name
```powershell
aws elbv2 describe-load-balancers `
  --names incident-commander-alb `
  --region $AWS_REGION `
  --query 'LoadBalancers[0].DNSName' `
  --output text
```

### 2. Test API
```powershell
$ALB_DNS = "your-alb-dns-here.us-east-1.elb.amazonaws.com"
curl "http://$ALB_DNS/docs"  # Access Swagger docs
```

### 3. Configure Custom Domain (Optional)
```powershell
# Create Route 53 record pointing to ALB
aws route53 change-resource-record-sets `
  --hosted-zone-id Z1234567890ABC `
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "'$ALB_DNS'",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'
```

### 4. Setup SSL/TLS (Recommended)
```powershell
# Request ACM certificate
aws acm request-certificate `
  --domain-name api.yourdomain.com `
  --validation-method DNS `
  --region $AWS_REGION
```

---

## Monitoring

### View Logs
```powershell
# Real-time logs
aws logs tail /ecs/incident-commander --follow --region $AWS_REGION

# Last 100 lines
aws logs tail /ecs/incident-commander --max-items 100 --region $AWS_REGION
```

### Check Service Status
```powershell
aws ecs describe-services `
  --cluster incident-commander `
  --services incident-commander-api `
  --region $AWS_REGION `
  --query 'services[0].[status,runningCount,desiredCount]' `
  --output text
```

### View CloudWatch Metrics
```powershell
aws cloudwatch get-metric-statistics `
  --namespace AWS/ECS `
  --metric-name CPUUtilization `
  --dimensions Name=ClusterName,Value=incident-commander `
  --statistics Average `
  --start-time 2024-01-01T00:00:00Z `
  --end-time 2024-01-02T00:00:00Z `
  --period 3600 `
  --region $AWS_REGION
```

---

## Cleanup (Delete Everything)

```powershell
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name $STACK_NAME --region $AWS_REGION

# Delete ECR images
aws ecr delete-repository `
  --repository-name incident-commander-backend `
  --force `
  --region $AWS_REGION

# Delete S3 buckets
aws s3 rb s3://$S3_BUCKET --force
aws s3 rb s3://$CF_BUCKET --force

# Delete secrets
aws secretsmanager delete-secret `
  --secret-id incident-commander/groq-key `
  --force-delete-without-recovery `
  --region $AWS_REGION
```

---

## Troubleshooting

### Tasks Not Starting
```powershell
# Check task failures
aws ecs describe-tasks `
  --cluster incident-commander `
  --tasks $(aws ecs list-tasks --cluster incident-commander --query 'taskArns[0]' --output text) `
  --region $AWS_REGION

# View logs
aws logs tail /ecs/incident-commander --follow --region $AWS_REGION
```

### Cannot Access API
```powershell
# Verify ALB is active
aws elbv2 describe-load-balancers --names incident-commander-alb --region $AWS_REGION

# Check target health
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:$AWS_REGION:$AWS_ACCOUNT_ID:targetgroup/incident-commander-tg/xyz --region $AWS_REGION

# Check security groups
aws ec2 describe-security-groups --group-ids $SG_ID --region $AWS_REGION
```

### High Costs
```powershell
# Check running resources
aws ecs describe-services --cluster incident-commander --services incident-commander-api --region $AWS_REGION

# Review CloudWatch metrics for optimization opportunities
aws cloudwatch list-metrics --namespace AWS/ECS --region $AWS_REGION
```

---

## Cost Estimation

| Component | Estimated Cost | Notes |
|-----------|----------------|-------|
| ECS Fargate (2 tasks) | $30-50/month | 256 CPU, 512 MB RAM |
| ALB | $15-20/month | Minimal usage |
| CloudWatch Logs | $5-10/month | 30-day retention |
| ECR | $0.50/month | Low storage |
| S3 Frontend | $1-5/month | Minimal storage |
| **Total** | **$50-85/month** | For staging environment |

**Production** typically costs 2-3x more due to higher capacity needs.

---

## Next Steps

1. ✅ Deploy application
2. ⬜ Set up custom domain (Route 53 + ACM)
3. ⬜ Configure CI/CD pipeline (CodePipeline)
4. ⬜ Set up monitoring alerts (SNS)
5. ⬜ Configure auto-scaling policies
6. ⬜ Set up backup strategy
7. ⬜ Implement WAF (Web Application Firewall)

---

## Support

For detailed information, see `AWS_DEPLOYMENT_GUIDE.md`
