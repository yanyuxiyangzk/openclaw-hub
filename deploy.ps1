# OpenClawHub Deploy Script (Windows PowerShell)
# Usage: .\deploy.ps1 [-Env staging|production]

param(
    [string]$Env = "staging"
)

$ErrorActionPreference = "Stop"

$PROJECT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $PROJECT_ROOT

Write-Host "=== OpenClawHub Deploy Script ===" -ForegroundColor Green

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker: $dockerVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Docker is not installed or not running" -ForegroundColor Red
    exit 1
}

# Check docker-compose
try {
    $dcVersion = docker-compose --version 2>&1
    Write-Host "docker-compose: $dcVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: docker-compose is not installed" -ForegroundColor Red
    exit 1
}

# Load environment variables
$envFile = if (Test-Path ".env.$Env") { ".env.$Env" } elseif (Test-Path ".env") { ".env" } else { $null }
if ($envFile) {
    Write-Host "Loading $envFile" -ForegroundColor Cyan
    Get-Content $envFile | Where-Object { $_ -notmatch '^#' -and $_ -match '=' } | ForEach-Object {
        $parts = $_.Split('=', 2)
        [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim(), 'Process')
    }
}

# Build and deploy
Write-Host "Building Docker images..." -ForegroundColor Green
docker-compose -f docker/docker-compose.prod.yml build

Write-Host "Starting services..." -ForegroundColor Green
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for services
Write-Host "Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check health
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    $statusCode = $health.StatusCode
} catch {
    $statusCode = 0
}

if ($statusCode -eq 200) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:8080"
    Write-Host "API: http://localhost:8080/api"
    Write-Host "Health: http://localhost:8080/health"
} else {
    Write-Host "Health check failed (HTTP $statusCode)" -ForegroundColor Red
    docker-compose -f docker/docker-compose.prod.yml logs
    exit 1
}

Write-Host "=== Deploy Complete ===" -ForegroundColor Green
