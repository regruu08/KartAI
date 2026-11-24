# ==============================================================================
# ReturnZero AI - Windows PowerShell Developer Utility
# Team BioXtreme | Code to Cart Round 2 Buildathon
# ==============================================================================

param(
    [ValidateSet("dev", "backend", "frontend", "lint", "typecheck", "test", "build", "verify", "help")]
    [string]$Action = "dev"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Show-Help {
    Write-Host "ReturnZero AI - PowerShell Dev Commands" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ".\scripts\dev.ps1 -Action dev        : Run backend and frontend concurrently in separate windows"
    Write-Host ".\scripts\dev.ps1 -Action backend    : Run FastAPI backend server (port 8000)"
    Write-Host ".\scripts\dev.ps1 -Action frontend   : Run Next.js frontend server (port 3000)"
    Write-Host ".\scripts\dev.ps1 -Action lint       : Run ruff (backend) and eslint (frontend)"
    Write-Host ".\scripts\dev.ps1 -Action typecheck  : Run mypy --strict (backend) and tsc (frontend)"
    Write-Host ".\scripts\dev.ps1 -Action test       : Run pytest and vitest"
    Write-Host ".\scripts\dev.ps1 -Action build      : Run next build (frontend)"
    Write-Host ".\scripts\dev.ps1 -Action verify     : Run full verification suite"
}

switch ($Action) {
    "help" {
        Show-Help
    }
    "backend" {
        Write-Host "Starting FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Green
        Set-Location "$RepoRoot\backend"
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
    }
    "frontend" {
        Write-Host "Starting Next.js frontend on http://localhost:3000..." -ForegroundColor Green
        Set-Location "$RepoRoot\frontend"
        npm run dev
    }
    "dev" {
        Write-Host "Launching backend and frontend in separate background processes..." -ForegroundColor Green
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\backend'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$RepoRoot\frontend'; npm run dev"
        Write-Host "Both processes launched! Backend: http://127.0.0.1:8000 | Frontend: http://localhost:3000" -ForegroundColor Cyan
    }
    "lint" {
        Write-Host "==> Linting Backend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\backend"
        python -m ruff check .
        python -m ruff format --check .
        Write-Host "==> Linting Frontend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\frontend"
        npm run lint
        Write-Host "[OK] Linting passed." -ForegroundColor Green
    }
    "typecheck" {
        Write-Host "==> Typechecking Backend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\backend"
        python -m mypy --strict app
        python -m mypy tests
        Write-Host "==> Typechecking Frontend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\frontend"
        npx tsc --noEmit
        Write-Host "[OK] Type checking passed." -ForegroundColor Green
    }
    "test" {
        Write-Host "==> Testing Backend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\backend"
        python -m pytest tests/ --cov=app --cov-report=term-missing
        Write-Host "==> Testing Frontend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\frontend"
        npm run test
        Write-Host "[OK] Tests passed." -ForegroundColor Green
    }
    "build" {
        Write-Host "==> Building Frontend..." -ForegroundColor Yellow
        Set-Location "$RepoRoot\frontend"
        npm run build
        Write-Host "[OK] Build passed." -ForegroundColor Green
    }
    "verify" {
        Write-Host "==> Running Full Verification Suite..." -ForegroundColor Cyan
        & "$PSScriptRoot\dev.ps1" -Action lint
        & "$PSScriptRoot\dev.ps1" -Action typecheck
        & "$PSScriptRoot\dev.ps1" -Action test
        & "$PSScriptRoot\dev.ps1" -Action build
        Set-Location "$RepoRoot"
        python scripts/check_claims.py
        python scripts/smoke_test.py
        Write-Host "[SUCCESS] All verification gates passed!" -ForegroundColor Green
    }
}
