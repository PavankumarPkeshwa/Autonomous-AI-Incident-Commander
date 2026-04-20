# AWS Deployment Guide for Autonomous Incident Commander

## Overview
This guide covers deploying the full-stack application (Python FastAPI backend + React frontend) to AWS.

**Recommended Architecture:**
- **Frontend**: CloudFront + S3 (static hosting)
- **Backend API**: ECS Fargate (containerized Python app)
- **Database**: DynamoDB or RDS (if adding persistence)
- **CI/CD**: CodePipeline + CodeBuild
- **Monitoring**: CloudWatch
- **Secrets**: AWS Secrets Manager

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Phase 1: Prepare Application](#phase-1-prepare-application)
3. [Phase 2: Backend Deployment (ECS Fargate)](#phase-2-backend-deployment-ecs-fargate)
4. [Phase 3: Frontend Deployment (S3 + CloudFront)](#phase-3-frontend-deployment-s3--cloudfront)
5. [Phase 4: CI/CD Pipeline](#phase-4-cicd-pipeline)
6. [Phase 5: Monitoring & Security](#phase-5-monitoring--security)
7. [Cost Optimization](#cost-optimization)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required AWS Services
- AWS Account with appropriate permissions
- AWS CLI v2 installed and configured
- IAM user with permissions for: ECS, ECR, S3, CloudFront, RDS/DynamoDB, CloudWatch, CodePipeline

### Local Tools
- Docker (for building container images)
- Node.js 18+ (for building frontend)
- Python 3.9+ (for backend)
- Git (for version control)

### Installation Commands (Windows PowerShell)
```powershell
# AWS CLI
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Docker Desktop
# Download from https://www.docker.com/products/docker-desktop

# Verify installations
aws --version
docker --version
node --version
```

---

## Phase 1: Prepare Application

### Step 1.1: Create `.dockerignore` for Backend
Create file: `Dockerfile.backend` (in root directory)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 1.2: Create `.dockerignore`
```
__pycache__
*.pyc
.git
.gitignore
.env
.env.local
node_modules
dist
build
*.log
.DS_Store
```

### Step 1.3: Create `.env.example`
```
# LLM Configuration
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=mixtral-8x7b-32768

# API Configuration
API_PORT=8000
API_HOST=0.0.0.0

# Frontend URL (for CORS)
FRONTEND_URL=https://your-frontend-domain.com
```

### Step 1.4: Update `requirements.txt` with Production Dependencies
```
langgraph>=0.0.1
langchain>=0.1.0
langchain-groq>=0.1.0
pydantic>=2.0
python-dotenv>=1.0
requests>=2.31
json5>=0.9
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
gunicorn>=21.2.0
boto3>=1.26.0
```

### Step 1.5: Build Frontend
```powershell
cd ui
npm install
npm run build
# Creates 'dist/' folder with optimized assets
```

---

## Phase 2: Backend Deployment (ECS Fargate)

### Step 2.1: Create ECR Repository
```powershell
# Set variables
$AWS_REGION = "us-east-1"
$AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
$ECR_REPO_NAME = "incident-commander-backend"

# Create ECR repository
aws ecr create-repository `
  --repository-name $ECR_REPO_NAME `
  --region $AWS_REGION

# Output will show repository URI like:
# 123456789.dkr.ecr.us-east-1.amazonaws.com/incident-commander-backend
```

### Step 2.2: Build and Push Docker Image
```powershell
# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login `
  --username AWS `
  --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build image
$ECR_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME"
docker build -f Dockerfile.backend -t $ECR_REPO_NAME:latest .

# Tag image
docker tag "${ECR_REPO_NAME}:latest" "${ECR_URI}:latest"
docker tag "${ECR_REPO_NAME}:latest" "${ECR_URI}:v1.0"

# Push to ECR
docker push "${ECR_URI}:latest"
docker push "${ECR_URI}:v1.0"
```

### Step 2.3: Create ECS Cluster
```powershell
# Create cluster
aws ecs create-cluster `
  --cluster-name incident-commander `
  --region $AWS_REGION

# Create CloudWatch log group
aws logs create-log-group `
  --log-group-name /ecs/incident-commander `
  --region $AWS_REGION
```

### Step 2.4: Create ECS Task Definition
Save as `ecs-task-definition.json`:
```json
{
  "family": "incident-commander-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "incident-commander",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/incident-commander-backend:latest",
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
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "API_HOST",
          "value": "0.0.0.0"
        },
        {
          "name": "API_PORT",
          "value": "8000"
        }
      ],
      "secrets": [
        {
          "name": "GROQ_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789:secret:incident-commander/groq-key:GROQ_API_KEY::"
        }
      ]
    }
  ]
}
```

### Step 2.5: Store Secrets in Secrets Manager
```powershell
# Store GROQ API Key
aws secretsmanager create-secret `
  --name incident-commander/groq-key `
  --secret-string '{
    "GROQ_API_KEY": "your-actual-groq-key-here"
  }' `
  --region $AWS_REGION
```

### Step 2.6: Create Load Balancer (ALB)
```powershell
# Get VPC ID
$VPC_ID = aws ec2 describe-vpcs `
  --filters "Name=isDefault,Values=true" `
  --query "Vpcs[0].VpcId" `
  --output text

# Get Subnet IDs
$SUBNETS = aws ec2 describe-subnets `
  --filters "Name=vpc-id,Values=$VPC_ID" `
  --query "Subnets[0:2].SubnetId" `
  --output text

# Create ALB
$ALB_ARN = aws elbv2 create-load-balancer `
  --name incident-commander-alb `
  --subnets $SUBNETS.Split() `
  --region $AWS_REGION `
  --query "LoadBalancers[0].LoadBalancerArn" `
  --output text

# Create Security Group for ALB
$SG_ID = aws ec2 create-security-group `
  --group-name incident-commander-alb-sg `
  --description "ALB security group" `
  --vpc-id $VPC_ID `
  --query "GroupId" `
  --output text

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 80 `
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress `
  --group-id $SG_ID `
  --protocol tcp `
  --port 443 `
  --cidr 0.0.0.0/0
```

### Step 2.7: Create Target Group
```powershell
# Create target group
aws elbv2 create-target-group `
  --name incident-commander-tg `
  --protocol HTTP `
  --port 8000 `
  --vpc-id $VPC_ID `
  --target-type ip `
  --region $AWS_REGION
```

### Step 2.8: Create ECS Service
```powershell
# Register task definition
aws ecs register-task-definition `
  --cli-input-json file://ecs-task-definition.json `
  --region $AWS_REGION

# Create ECS service
aws ecs create-service `
  --cluster incident-commander `
  --service-name incident-commander-api `
  --task-definition incident-commander-backend:1 `
  --desired-count 2 `
  --launch-type FARGATE `
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS],securityGroups=[$SG_ID],assignPublicIp=ENABLED}" `
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:$AWS_REGION:$AWS_ACCOUNT_ID:targetgroup/incident-commander-tg/xyz,containerName=incident-commander,containerPort=8000 `
  --region $AWS_REGION
```

---

## Phase 3: Frontend Deployment (S3 + CloudFront)

### Step 3.1: Create S3 Bucket for Frontend
```powershell
$S3_BUCKET = "incident-commander-frontend-$(Get-Random -Minimum 10000 -Maximum 99999)"

# Create bucket
aws s3api create-bucket `
  --bucket $S3_BUCKET `
  --region $AWS_REGION

# Enable versioning
aws s3api put-bucket-versioning `
  --bucket $S3_BUCKET `
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block `
  --bucket $S3_BUCKET `
  --public-access-block-configuration `
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Step 3.2: Upload Frontend Build to S3
```powershell
# Build React app
cd ui
npm run build

# Sync to S3
aws s3 sync dist/ s3://$S3_BUCKET/ `
  --delete `
  --cache-control "max-age=31536000" `
  --exclude "index.html"

aws s3 cp dist/index.html s3://$S3_BUCKET/index.html `
  --cache-control "no-cache" `
  --content-type "text/html"
```

### Step 3.3: Create CloudFront Distribution
Save as `cloudfront-distribution.json`:
```json
{
  "CallerReference": "incident-commander-2024",
  "Comment": "Autonomous Incident Commander Frontend",
  "DefaultRootObject": "index.html",
  "Origins": {
    "Items": [
      {
        "Id": "S3Origin",
        "DomainName": "incident-commander-frontend-xxxxx.s3.us-east-1.amazonaws.com",
        "S3OriginConfig": {}
      }
    ],
    "Quantity": 1
  },
  "DefaultCacheBehavior": {
    "AllowedMethods": {
      "Items": ["GET", "HEAD"],
      "Quantity": 2
    },
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "Compress": true,
    "TargetOriginId": "S3Origin",
    "ViewerProtocolPolicy": "redirect-to-https"
  },
  "Enabled": true,
  "PriceClass": "PriceClass_100",
  "ViewerProtocolPolicy": "redirect-to-https"
}
```

```powershell
# Create distribution
aws cloudfront create-distribution `
  --distribution-config file://cloudfront-distribution.json `
  --region $AWS_REGION
```

---

## Phase 4: CI/CD Pipeline

### Step 4.1: Create CodeBuild Project for Backend
Save as `buildspec.yml` (root directory):
```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo "Logging in to Amazon ECR..."
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/incident-commander-backend
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}
  
  build:
    commands:
      - echo "Building Docker image..."
      - docker build -f Dockerfile.backend -t $REPOSITORY_URI:$IMAGE_TAG .
      - docker tag $REPOSITORY_URI:$IMAGE_TAG $REPOSITORY_URI:latest
  
  post_build:
    commands:
      - echo "Pushing Docker image to ECR..."
      - docker push $REPOSITORY_URI:$IMAGE_TAG
      - docker push $REPOSITORY_URI:latest
      - echo "Writing image definitions file..."
      - printf '[{"name":"incident-commander","imageUri":"%s"}]' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files: imagedefinitions.json
```

### Step 4.2: Create CodeBuild Project for Frontend
Create `buildspec-frontend.yml`:
```yaml
version: 0.2

phases:
  install:
    commands:
      - echo "Installing dependencies..."
      - cd ui && npm install
  
  build:
    commands:
      - echo "Building React app..."
      - npm run build
  
  post_build:
    commands:
      - echo "Uploading to S3..."
      - aws s3 sync dist/ s3://$S3_BUCKET/ --delete --cache-control "max-age=31536000" --exclude "index.html"
      - aws s3 cp dist/index.html s3://$S3_BUCKET/index.html --cache-control "no-cache" --content-type "text/html"
      - echo "Invalidating CloudFront distribution..."
      - aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DIST_ID --paths "/*"

cache:
  paths:
    - ui/node_modules/**/*
```

### Step 4.3: Create CodePipeline
```powershell
# Create pipeline (via Console or AWS CLI)
# GitHub → CodeBuild (Backend) → CodeBuild (Frontend) → Deploy to ECS

# Recommended steps:
# 1. Source: GitHub repository
# 2. Build: CodeBuild (buildspec.yml for backend)
# 3. Build: CodeBuild (buildspec-frontend.yml for frontend)
# 4. Deploy: CodeDeploy to ECS
```

---

## Phase 5: Monitoring & Security

### Step 5.1: Set Up CloudWatch Alarms
```powershell
# CPU Utilization Alarm
aws cloudwatch put-metric-alarm `
  --alarm-name incident-commander-high-cpu `
  --alarm-description "Alert when CPU exceeds 80%" `
  --metric-name CPUUtilization `
  --namespace AWS/ECS `
  --statistic Average `
  --period 300 `
  --threshold 80 `
  --comparison-operator GreaterThanThreshold `
  --evaluation-periods 2

# Memory Utilization Alarm
aws cloudwatch put-metric-alarm `
  --alarm-name incident-commander-high-memory `
  --alarm-description "Alert when memory exceeds 90%" `
  --metric-name MemoryUtilization `
  --namespace AWS/ECS `
  --statistic Average `
  --period 300 `
  --threshold 90 `
  --comparison-operator GreaterThanThreshold `
  --evaluation-periods 2
```

### Step 5.2: Enable VPC Flow Logs
```powershell
# For enhanced security and troubleshooting
aws ec2 create-flow-logs `
  --resource-type VPC `
  --resource-ids $VPC_ID `
  --traffic-type ALL `
  --log-destination-type cloud-watch-logs `
  --log-group-name /aws/vpc/flowlogs
```

### Step 5.3: Enable WAF (Optional)
```powershell
# Create WAF Web ACL for CloudFront
# Protects against common attacks (SQL injection, XSS, etc.)
# Can be set up via AWS Console or CloudFormation
```

---

## Cost Optimization

### 1. Use AWS Savings Plans
- 1-year or 3-year commitment for ECS Fargate
- Reduce costs by up to 52%

### 2. Right-size ECS Resources
```
Current: cpu=256, memory=512 (minimal)
Review after 1-2 weeks and adjust based on CloudWatch metrics
```

### 3. Use S3 Intelligent-Tiering
```powershell
aws s3api put-bucket-intelligent-tiering-configuration `
  --bucket $S3_BUCKET `
  --id AutoTierConfig `
  --intelligent-tiering-configuration file://config.json
```

### 4. Compress Images
- Ensure Docker images are optimized
- Use multi-stage builds in Dockerfile

### 5. Monitor Costs
```powershell
# Set up AWS Budgets
aws budgets create-budget `
  --account-id $AWS_ACCOUNT_ID `
  --budget file://budget.json
```

---

## Deployment Checklist

- [ ] Prerequisites installed (AWS CLI, Docker, Node.js)
- [ ] AWS credentials configured
- [ ] Environment variables (.env file) prepared
- [ ] Docker image built and tested locally
- [ ] Frontend built and tested locally
- [ ] ECR repository created
- [ ] Docker image pushed to ECR
- [ ] ECS cluster created
- [ ] Task definition registered
- [ ] Load balancer configured
- [ ] ECS service created with 2+ replicas
- [ ] S3 bucket created and frontend uploaded
- [ ] CloudFront distribution created
- [ ] Secrets Manager configured with API keys
- [ ] CloudWatch log groups created
- [ ] CloudWatch alarms configured
- [ ] CI/CD pipeline configured (optional)
- [ ] Custom domain configured (Route 53)
- [ ] SSL certificate configured (ACM)
- [ ] Tested end-to-end in staging environment
- [ ] Production deployment executed

---

## Estimated AWS Monthly Costs

```
ECS Fargate (2 tasks, 256 CPU, 512 MB): $30-40
ALB: $15-25
S3 Storage (frontend): $1-3
CloudFront (based on traffic): $10-50+
CloudWatch (logs): $5-10
Secrets Manager: $0.40
Total Estimate: $60-130/month (low traffic)
```

---

## Troubleshooting

### Task Fails to Start
1. Check CloudWatch logs: `/ecs/incident-commander`
2. Verify ECR image exists and is accessible
3. Check task IAM role permissions
4. Verify environment variables and secrets

### Cannot Connect to API
1. Check security group allows inbound on port 8000
2. Verify ALB health check status
3. Check ALB target group registrations
4. Test with: `curl http://alb-dns:8000/docs`

### Frontend Blank Page
1. Check browser console for CORS errors
2. Verify API endpoint in frontend config
3. Check CloudFront cache invalidation
4. Verify index.html has correct API_URL

### High Cost
1. Review CloudWatch metrics for resource usage
2. Check for unattached volumes or instances
3. Review data transfer charges
4. Optimize CloudFront cache behavior

---

## Next Steps

1. **Domain & SSL**: Configure Route 53 and ACM for custom domain
2. **Auto-Scaling**: Set up ECS auto-scaling based on CPU/memory
3. **RDS Integration**: Add database if persistence needed
4. **API Gateway**: Consider API Gateway for rate limiting
5. **Lambda**: Migrate background tasks to Lambda
6. **Backup Strategy**: Set up automated snapshots

