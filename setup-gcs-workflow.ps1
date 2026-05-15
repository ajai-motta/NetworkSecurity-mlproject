# GCS Upload Workflow Setup Helper (PowerShell)
# This script helps configure GitHub secrets for GCS uploads on Windows

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
    $gsutil_installed = $null -ne (Get-Command gsutil -ErrorAction SilentlyContinue)
    
    if ($gcloud_installed) {
        Write-Success "Google Cloud SDK installed"
    } else {
        Write-Error "Google Cloud SDK not found"
        Write-Host "Download from: https://cloud.google.com/sdk/docs/install"
    }
    
    if ($gsutil_installed) {
        Write-Success "gsutil available"
    } else {
        Write-Warning "gsutil not accessible (may need to restart PowerShell)"
    }
    
    Write-Host ""
}

function Get-ProjectIdFromKey {
    param([string]$KeyFilePath)
    
    if (-not (Test-Path $KeyFilePath)) {
        Write-Error "File not found: $KeyFilePath"
        return $null
    }
    
    try {
        $keyContent = Get-Content $KeyFilePath | ConvertFrom-Json
        return $keyContent.project_id
    } catch {
        Write-Error "Failed to parse JSON: $_"
        return $null
    }
}

function Validate-KeyFile {
    param([string]$KeyFilePath)
    
    if (-not (Test-Path $KeyFilePath)) {
        Write-Error "File not found: $KeyFilePath"
        return $false
    }
    
    try {
        $keyContent = Get-Content $KeyFilePath | ConvertFrom-Json
        
        $required = @("type", "project_id", "private_key", "client_email")
        foreach ($field in $required) {
            if (-not $keyContent.$field) {
                Write-Error "Missing required field: $field"
                return $false
            }
        }
        
        Write-Success "Key file is valid"
        return $true
    } catch {
        Write-Error "Invalid JSON format: $_"
        return $false
    }
}

function List-Buckets {
    Write-Host "Available GCS Buckets:"
    Write-Host "====================="
    
    try {
        gsutil ls
    } catch {
        Write-Error "Failed to list buckets. Ensure you're authenticated with: gcloud auth login"
    }
    
    Write-Host ""
}

function Create-Bucket {
    param(
        [string]$BucketName,
        [string]$Region = "us-central1"
    )
    
    Write-Host "Creating bucket: gs://$BucketName in $Region"
    
    try {
        gsutil mb -l $Region "gs://$BucketName"
        Write-Success "Bucket created"
        
        Write-Host "Enabling versioning..."
        gsutil versioning set on "gs://$BucketName"
        Write-Success "Versioning enabled"
    } catch {
        Write-Error "Failed to create bucket: $_"
    }
}

function Show-ManualSetup {
    param(
        [string]$KeyFilePath,
        [string]$ProjectId,
        [string]$BucketName
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
    Write-Host "Value: (Contents of your service account JSON key file)"
    Write-Host "Path: $KeyFilePath"
    Write-Host ""
    
    Write-Host "Secret 2: GCP_PROJECT_ID" -ForegroundColor Yellow
    Write-Host "Value: $ProjectId"
    Write-Host ""
    
    Write-Host "Secret 3: GCS_BUCKET_NAME" -ForegroundColor Yellow
    Write-Host "Value: $BucketName"
    Write-Host ""
    
    Write-Warning "Action Required:"
    Write-Host "Please add these secrets manually at:"
    Write-Host "https://github.com/[YOUR_ORG]/[YOUR_REPO]/settings/secrets/actions" -ForegroundColor Cyan
}

function Show-GhCliSetup {
    param(
        [string]$KeyFilePath,
        [string]$ProjectId,
        [string]$BucketName
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
        
        $BucketName | gh secret set GCS_BUCKET_NAME
        Write-Success "GCS_BUCKET_NAME secret added"
        
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
    Write-Header "Full Automatic Setup"
    
    # Get key file path
    $keyFile = Read-Host "Path to service account JSON key file"
    
    if (-not (Validate-KeyFile $keyFile)) {
        return
    }
    
    $projectId = Get-ProjectIdFromKey $keyFile
    Write-Success "Project ID: $projectId"
    
    Write-Host ""
    List-Buckets
    
    $bucketName = Read-Host "Enter GCS bucket name (or press Enter to create new)"
    
    if ([string]::IsNullOrEmpty($bucketName)) {
        $bucketName = Read-Host "New bucket name"
        $region = Read-Host "Region (default: us-central1)"
        if ([string]::IsNullOrEmpty($region)) { $region = "us-central1" }
        Create-Bucket $bucketName $region
    }
    
    Write-Host ""
    
    # Try GitHub CLI first
    $useGhCli = Read-Host "Use GitHub CLI to set secrets? (y/n)"
    if ($useGhCli -eq "y") {
        if (Show-GhCliSetup $keyFile $projectId $bucketName) {
            Write-Host ""
            Write-Success "Setup complete!"
        } else {
            Show-ManualSetup $keyFile $projectId $bucketName
        }
    } else {
        Show-ManualSetup $keyFile $projectId $bucketName
    }
    
    Write-Host ""
    Write-Success "Next steps:"
    Write-Host "1. Verify secrets are in GitHub Settings"
    Write-Host "2. Push changes to trigger workflow: git push"
    Write-Host "3. Monitor in GitHub Actions tab"
    Write-Host "4. Verify upload with: gsutil ls -r gs://$bucketName/models/"
}

function Show-Menu {
    Write-Header "Setup Options"
    Write-Host "1. Check prerequisites"
    Write-Host "2. List existing GCS buckets"
    Write-Host "3. Create new GCS bucket"
    Write-Host "4. Validate service account key file"
    Write-Host "5. Show manual setup instructions"
    Write-Host "6. Full automatic setup"
    Write-Host "7. Open GitHub Repository Settings"
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
Write-Header "GCS Upload Workflow Setup (PowerShell)"

Check-Prerequisites

$continue = $true
while ($continue) {
    Show-Menu
    $option = Read-Host "Select option (0-7)"
    
    switch ($option) {
        "1" {
            Check-Prerequisites
        }
        "2" {
            List-Buckets
        }
        "3" {
            $bucketName = Read-Host "Bucket name"
            $region = Read-Host "Region (default: us-central1)"
            if ([string]::IsNullOrEmpty($region)) { $region = "us-central1" }
            Create-Bucket $bucketName $region
        }
        "4" {
            $keyFile = Read-Host "Path to service account JSON key"
            Validate-KeyFile $keyFile
            if ((Test-Path $keyFile)) {
                $projectId = Get-ProjectIdFromKey $keyFile
                Write-Host "Project ID: $projectId"
            }
        }
        "5" {
            $keyFile = Read-Host "Path to service account JSON key"
            if (Validate-KeyFile $keyFile) {
                $bucketName = Read-Host "GCS bucket name"
                $projectId = Get-ProjectIdFromKey $keyFile
                Show-ManualSetup $keyFile $projectId $bucketName
            }
        }
        "6" {
            Full-Setup
        }
        "7" {
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
