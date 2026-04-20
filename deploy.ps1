# AWS Deployment Automation Script
# This script automates the deployment of the Autonomous Incident Commander to AWS

param(
    [string]$Action = "help",
    [string]$Environment = "staging",
    [string]$Region = "us-east-1",
    [string]$ClusterName = "incident-commander",
    [string]$ServiceName = "incident-commander-api",
    [string]$RepositoryName = "incident-commander-backend"
)

# Color output
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

# Get AWS Account ID
function Get-AWSAccountId {
    Write-Info "Fetching AWS Account ID..."
    $AccountId = aws sts get-caller-identity --query Account --output text
    if ($LASTEXITCODE -eq 0) {
        Write-Success "AWS Account ID: $AccountId"
        return $AccountId
    } else {
        Write-Error-Custom "Failed to get AWS Account ID. Ensure AWS CLI is configured."
        exit 1
    }
}

# Check prerequisites
function Check-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    $tools = @("docker", "node", "npm", "aws", "git")
    foreach ($tool in $tools) {
        try {
            $version = & $tool --version 2>$null
            Write-Success "$tool is installed"
        } catch {
            Write-Error-Custom "$tool is not installed"
            exit 1
        }
    }
}

# Build backend Docker image
function Build-Backend {
    param([string]$AccountId)
    
    Write-Info "Building backend Docker image..."
    $ImageUri = "$AccountId.dkr.ecr.$Region.amazonaws.com/$RepositoryName"
    
    try {
        docker build -f Dockerfile -t $RepositoryName:latest .
        Write-Success "Backend image built successfully"
        
        docker tag "${RepositoryName}:latest" "${ImageUri}:latest"
        docker tag "${RepositoryName}:latest" "${ImageUri}:$((Get-Date).ToString('yyyyMMdd-HHmmss'))"
        Write-Success "Image tagged with ECR URI"
        
        return $ImageUri
    } catch {
        Write-Error-Custom "Failed to build backend image: $_"
        exit 1
    }
}

# Push image to ECR
function Push-ToECR {
    param(
        [string]$AccountId,
        [string]$ImageUri
    )
    
    Write-Info "Authenticating with ECR..."
    try {
        $LoginToken = aws ecr get-login-password --region $Region
        $LoginToken | docker login --username AWS --password-stdin "$AccountId.dkr.ecr.$Region.amazonaws.com"
        Write-Success "ECR authentication successful"
    } catch {
        Write-Error-Custom "Failed to authenticate with ECR: $_"
        exit 1
    }
    
    Write-Info "Pushing image to ECR..."
    try {
        docker push "${ImageUri}:latest"
        Write-Success "Image pushed to ECR successfully"
    } catch {
        Write-Error-Custom "Failed to push image to ECR: $_"
        exit 1
    }
}

# Build frontend
function Build-Frontend {
    Write-Info "Building frontend..."
    
    try {
        Push-Location ui
        npm install
        npm run build
        Pop-Location
        Write-Success "Frontend built successfully"
    } catch {
        Write-Error-Custom "Failed to build frontend: $_"
        exit 1
    }
}

# Deploy frontend to S3
function Deploy-Frontend-S3 {
    param([string]$S3Bucket)
    
    Write-Info "Deploying frontend to S3..."
    
    try {
        aws s3 sync ui/dist/ "s3://$S3Bucket/" `
            --delete `
            --cache-control "max-age=31536000" `
            --exclude "index.html" `
            --region $Region
        
        aws s3 cp ui/dist/index.html "s3://$S3Bucket/index.html" `
            --cache-control "no-cache" `
            --content-type "text/html" `
            --region $Region
        
        Write-Success "Frontend deployed to S3"
    } catch {
        Write-Error-Custom "Failed to deploy frontend: $_"
        exit 1
    }
}

# Update ECS service
function Update-ECSService {
    Write-Info "Updating ECS service..."
    
    try {
        aws ecs update-service `
            --cluster $ClusterName `
            --service $ServiceName `
            --force-new-deployment `
            --region $Region
        
        Write-Success "ECS service updated with new image"
        Write-Info "Waiting for service to stabilize..."
        
        aws ecs wait services-stable `
            --cluster $ClusterName `
            --services $ServiceName `
            --region $Region
        
        Write-Success "ECS service is stable"
    } catch {
        Write-Error-Custom "Failed to update ECS service: $_"
        exit 1
    }
}

# Check service health
function Check-ServiceHealth {
    Write-Info "Checking service health..."
    
    try {
        $ServiceInfo = aws ecs describe-services `
            --cluster $ClusterName `
            --services $ServiceName `
            --region $Region `
            --query 'services[0]' | ConvertFrom-Json
        
        $Status = $ServiceInfo.status
        $RunningCount = $ServiceInfo.runningCount
        $DesiredCount = $ServiceInfo.desiredCount
        
        Write-Host "Status: $Status"
        Write-Host "Running Tasks: $RunningCount / $DesiredCount"
        
        if ($RunningCount -eq $DesiredCount) {
            Write-Success "All tasks are running"
        } else {
            Write-Warning-Custom "Not all tasks are running yet"
        }
    } catch {
        Write-Error-Custom "Failed to check service health: $_"
    }
}

# Main deployment flow
function Deploy-Full {
    param([string]$AccountId)
    
    Write-Info "Starting full deployment to AWS ($Environment environment)"
    
    # Build and push backend
    $ImageUri = Build-Backend -AccountId $AccountId
    Push-ToECR -AccountId $AccountId -ImageUri $ImageUri
    
    # Build and deploy frontend
    Build-Frontend
    # Note: Update S3_BUCKET with your actual bucket name
    $S3Bucket = "incident-commander-frontend-$Environment"
    Deploy-Frontend-S3 -S3Bucket $S3Bucket
    
    # Update ECS service
    Update-ECSService
    
    # Check health
    Check-ServiceHealth
    
    Write-Success "Deployment completed successfully!"
}

# Help text
function Show-Help {
    Write-Host @"
╔════════════════════════════════════════════════════════════════╗
║   AWS Deployment Script for Autonomous Incident Commander     ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  .\deploy.ps1 -Action <action> -Environment <env> -Region <region>

ACTIONS:
  help              Show this help message
  check-prereq      Check if all prerequisites are installed
  build-backend     Build the backend Docker image
  build-frontend    Build the React frontend
  push-ecr          Build backend and push to ECR
  deploy-frontend   Build and deploy frontend to S3
  full-deployment   Complete end-to-end deployment
  check-health      Check service health status
  view-logs         View ECS service logs

PARAMETERS:
  -Action           The action to perform (default: help)
  -Environment      Environment name: staging or production (default: staging)
  -Region           AWS region (default: us-east-1)
  -ClusterName      ECS cluster name (default: incident-commander)
  -ServiceName      ECS service name (default: incident-commander-api)

EXAMPLES:
  # Check prerequisites
  .\deploy.ps1 -Action check-prereq

  # Full deployment to staging
  .\deploy.ps1 -Action full-deployment -Environment staging

  # Deploy to production
  .\deploy.ps1 -Action full-deployment -Environment production -Region us-east-1

  # Check service health
  .\deploy.ps1 -Action check-health

REQUIREMENTS:
  - AWS CLI v2
  - Docker Desktop
  - Node.js 18+
  - PowerShell 7+
  - Valid AWS credentials configured

"@
}

# Route actions
switch ($Action.ToLower()) {
    "help" {
        Show-Help
    }
    "check-prereq" {
        Check-Prerequisites
        Write-Success "All prerequisites are installed"
    }
    "build-backend" {
        Build-Backend -AccountId (Get-AWSAccountId)
    }
    "build-frontend" {
        Build-Frontend
    }
    "push-ecr" {
        $AccountId = Get-AWSAccountId
        $ImageUri = Build-Backend -AccountId $AccountId
        Push-ToECR -AccountId $AccountId -ImageUri $ImageUri
    }
    "deploy-frontend" {
        Build-Frontend
        # User needs to set S3 bucket
        Write-Warning-Custom "Please set your S3 bucket name in the script"
    }
    "full-deployment" {
        Check-Prerequisites
        $AccountId = Get-AWSAccountId
        Deploy-Full -AccountId $AccountId
    }
    "check-health" {
        Check-ServiceHealth
    }
    "view-logs" {
        Write-Info "Viewing recent logs..."
        aws logs tail "/ecs/$ClusterName" --follow --region $Region
    }
    default {
        Write-Error-Custom "Unknown action: $Action"
        Write-Host "Run '.\deploy.ps1 -Action help' for usage information"
        exit 1
    }
}
