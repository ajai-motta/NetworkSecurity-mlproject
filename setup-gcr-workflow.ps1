# GCR Push Workflow Setup Helper (PowerShell)
# This script helps configure GitHub secrets for GCR uploads on Windows

function Write-Header {
    param([string]$Text)
    Write-Host "======================================"
    Write-Host $Text -ForegroundColor Cyan -BackgroundColor Black
    Write-Host "======================================"
}

function Write-Success {
    param([string]$Text)
    Write-Host "✓ $Text" -ForegroundColor Green
}

function Write-Error {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Check-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $gcloud_installed = $null -ne (Get-Command gcloud -ErrorAction SilentlyContinue)
    $docker_installed = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)
    
    if ($gcloud_installed) {
        Write-Success "Google Cloud SDK installed"
    } else {
        Write-Error "Google Cloud SDK not found"
        Write-Host "Download from: https://cloud.google.com/sdk/docs/install"
    }
    
    if ($docker_installed) {
        Write-Success "Docker installed"
    } else {
        Write-Warning "Docker not found (optional but recommended)"
    }
    
    Write-Host ""
}

function Enable-ContainerRegistryAPI {
    param([string]$ProjectId)
    
    Write-Host "Enabling Container Registry API..."
    
    try {
        gcloud services enable containerregistry.googleapis.com --project=$ProjectId
        Write-Success "Container Registry API enabled"
    } catch {
        Write-Error "Failed to enable API: $_"
    }
}

function Create-ServiceAccount {
    param(
        [string]$ProjectId,
        [string]$SAName
    )
    
    Write-Host "Creating service account: $SAName"
    
    try {
        gcloud iam service-accounts create $SAName `
            --display-name="GitHub Actions Container Registry" `
            --project=$ProjectId
        Write-Success "Service account created"
        return $true
    } catch {
        Write-Warning "Service account may already exist: $_"
        return $false
    }
}

function Grant-ServiceAccountRoles {
    param(
        [string]$ProjectId,
        [string]$SAName
    )
    
    Write-Host "Granting roles to service account..."
    
    $SA_EMAIL = "$SAName@$ProjectId.iam.gserviceaccount.com"
    
    try {
        # Grant storage admin
        gcloud projects add-iam-policy-binding $ProjectId `
            --member="serviceAccount:$SA_EMAIL" `
            --role="roles/storage.admin" `
            --quiet
        Write-Success "Storage Admin role granted"
        
        # Grant container developer
        gcloud projects add-iam-policy-binding $ProjectId `
            --member="serviceAccount:$SA_EMAIL" `
            --role="roles/container.developer" `
            --quiet
        Write-Success "Container Developer role granted"
        
    } catch {
        Write-Error "Failed to grant roles: $_"
        return $false
    }
    
    return $true
}

function Create-ServiceAccountKey {
    param(
        [string]$ProjectId,
        [string]$SAName,
        [string]$OutputFile
    )
    
    Write-Host "Creating service account key..."
    
    $SA_EMAIL = "$SAName@$ProjectId.iam.gserviceaccount.com"
    
    try {
        gcloud iam service-accounts keys create $OutputFile `
            --iam-account=$SA_EMAIL `
            --project=$ProjectId
        Write-Success "Service account key created: $OutputFile"
        return $true
    } catch {
        Write-Error "Failed to create key: $_"
        return $false
    }
}

function Show-ManualSetup {
    param(
        [string]$KeyFilePath,
        [string]$ProjectId
    )
    
    Write-Header "Manual GitHub Secret Setup"
    
    Write-Host ""
    Write-Host "1. Go to your GitHub repository"
    Write-Host "2. Settings > Secrets and variables > Actions"
    Write-Host "3. Click 'New repository secret'"
    Write-Host ""
    Write-Host "Add the following secrets:"
    Write-Host ""
    
    Write-Host "Secret 1: GCP_SA_KEY" -ForegroundColor Yellow
    Write-Host "Value: (Contents of service account JSON key)"
    Write-Host "Path: $KeyFilePath"
    Write-Host ""
    Write-Host "To copy the content:" -ForegroundColor Cyan
    Write-Host "Get-Content '$KeyFilePath' | Set-Clipboard"
    Write-Host ""
    
    Write-Host "Secret 2: GCP_PROJECT_ID" -ForegroundColor Yellow
    Write-Host "Value: $ProjectId"
    Write-Host ""
    
    Write-Warning "Action Required:"
    Write-Host "Please add these secrets manually at:"
    Write-Host "https://github.com/[YOUR_ORG]/[YOUR_REPO]/settings/secrets/actions" -ForegroundColor Cyan
}

function Show-GhCliSetup {
    param(
        [string]$KeyFilePath,
        [string]$ProjectId
    )
    
    Write-Header "GitHub CLI Secret Setup"
    
    $gh_installed = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)
    
    if (-not $gh_installed) {
        Write-Warning "GitHub CLI not installed"
        Write-Host "Install from: https://cli.github.com"
        return $false
    }
    
    Write-Host "Setting secrets in your GitHub repository..."
    Write-Host ""
    
    try {
        # Add secrets
        $keyContent = Get-Content $KeyFilePath -Raw
        $keyContent | gh secret set GCP_SA_KEY
        Write-Success "GCP_SA_KEY secret added"
        
        $ProjectId | gh secret set GCP_PROJECT_ID
        Write-Success "GCP_PROJECT_ID secret added"
        
        Write-Host ""
        Write-Host "Verifying secrets..."
        gh secret list
        
        return $true
    } catch {
        Write-Error "Failed to set secrets: $_"
        Write-Host "Ensure GitHub CLI is authenticated: gh auth login"
        return $false
    }
}

function Full-Setup {
    Write-Header "Full Automatic Setup for GCR"
    
    $projectId = Read-Host "Enter GCP Project ID"
    if ([string]::IsNullOrEmpty($projectId)) {
        Write-Error "Project ID is required"
        return
    }
    
    $saName = Read-Host "Enter Service Account name (default: github-actions-gcr)"
    if ([string]::IsNullOrEmpty($saName)) {
        $saName = "github-actions-gcr"
    }
    
    Write-Host ""
    
    # Enable API
    Enable-ContainerRegistryAPI $projectId
    Write-Host ""
    
    # Create service account
    Create-ServiceAccount $projectId $saName
    Write-Host ""
    
    # Grant roles
    Grant-ServiceAccountRoles $projectId $saName
    Write-Host ""
    
    # Create key
    $keyFile = Read-Host "Path to save key file (default: gcr-key.json)"
    if ([string]::IsNullOrEmpty($keyFile)) {
        $keyFile = "gcr-key.json"
    }
    
    Create-ServiceAccountKey $projectId $saName $keyFile
    Write-Host ""
    
    # Try GitHub CLI first
    $useGhCli = Read-Host "Use GitHub CLI to set secrets? (y/n)"
    if ($useGhCli -eq "y") {
        if (Show-GhCliSetup $keyFile $projectId) {
            Write-Host ""
            Write-Success "Setup complete!"
        } else {
            Show-ManualSetup $keyFile $projectId
        }
    } else {
        Show-ManualSetup $keyFile $projectId
    }
    
    Write-Host ""
    Write-Success "Next steps:"
    Write-Host "1. Verify secrets are in GitHub Settings"
    Write-Host "2. Push changes to trigger workflow: git push"
    Write-Host "3. Monitor in GitHub Actions tab"
    Write-Host "4. View image with: gcloud container images list-tags gcr.io/$projectId/network-security-model"
}

function Show-Menu {
    Write-Header "GCR Setup Options"
    Write-Host "1. Check prerequisites"
    Write-Host "2. Enable Container Registry API"
    Write-Host "3. Create service account"
    Write-Host "4. Grant service account roles"
    Write-Host "5. Create service account key"
    Write-Host "6. Show manual setup instructions"
    Write-Host "7. Full automatic setup"
    Write-Host "8. Open GitHub Repository Settings"
    Write-Host "0. Exit"
    Write-Host ""
}

function Open-GitHubSettings {
    $repo = Read-Host "Enter GitHub repository (owner/repo)"
    $url = "https://github.com/$repo/settings/secrets/actions"
    Start-Process $url
    Write-Success "Opened: $url"
}

# Main loop
Clear-Host
Write-Header "GCR Push Workflow Setup (PowerShell)"

Check-Prerequisites

$continue = $true
while ($continue) {
    Show-Menu
    $option = Read-Host "Select option (0-8)"
    
    switch ($option) {
        "1" {
            Check-Prerequisites
        }
        "2" {
            $projectId = Read-Host "GCP Project ID"
            Enable-ContainerRegistryAPI $projectId
        }
        "3" {
            $projectId = Read-Host "GCP Project ID"
            $saName = Read-Host "Service Account name"
            Create-ServiceAccount $projectId $saName
        }
        "4" {
            $projectId = Read-Host "GCP Project ID"
            $saName = Read-Host "Service Account name"
            Grant-ServiceAccountRoles $projectId $saName
        }
        "5" {
            $projectId = Read-Host "GCP Project ID"
            $saName = Read-Host "Service Account name"
            $outputFile = Read-Host "Output file path (default: gcr-key.json)"
            if ([string]::IsNullOrEmpty($outputFile)) { $outputFile = "gcr-key.json" }
            Create-ServiceAccountKey $projectId $saName $outputFile
        }
        "6" {
            $keyFile = Read-Host "Path to service account key"
            $projectId = Read-Host "GCP Project ID"
            Show-ManualSetup $keyFile $projectId
        }
        "7" {
            Full-Setup
        }
        "8" {
            Open-GitHubSettings
        }
        "0" {
            $continue = $false
            Write-Host "Exiting..."
        }
        default {
            Write-Error "Invalid option"
        }
    }
    
    if ($continue) {
        Read-Host "Press Enter to continue"
        Clear-Host
    }
}
