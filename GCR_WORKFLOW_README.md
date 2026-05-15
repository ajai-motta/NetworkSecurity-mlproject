# Docker Image to GCR Workflow - Complete Guide

## 📋 Overview

This workflow automatically builds your Docker image and pushes it to Google Container Registry (GCR) whenever you make changes, using GitHub repository secrets for secure credential management.

## 🚀 Quick Start

### Step 1: Enable Container Registry API
```bash
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Create Service Account & Key
```bash
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions-gcr"

# Create service account
gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions GCR"

# Grant roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

# Create and download key
gcloud iam service-accounts keys create gcr-key.json \
  --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 3: Add GitHub Secrets
1. Go to your GitHub repository
2. Settings > Secrets and variables > Actions
3. Create secrets:
   - `GCP_SA_KEY` - Contents of `gcr-key.json`
   - `GCP_PROJECT_ID` - Your GCP project ID

### Step 4: Test the Workflow
1. Go to Actions > Build and Push Docker Image to GCR
2. Click "Run workflow"
3. Monitor the build process

## 📁 Files Created

| File | Purpose |
|------|---------|
| `.github/workflows/push-to-gcr.yml` | Main workflow file |
| `GCR_SETUP_GUIDE.md` | Detailed setup instructions |
| `GCR_CONFIG_REFERENCE.md` | Configuration reference |
| `GCR_WORKFLOW_README.md` | This file |

## 🔑 Required GitHub Secrets

Create these in your GitHub repository (Settings > Secrets and variables > Actions):

```
GCP_SA_KEY          → JSON service account key
GCP_PROJECT_ID      → Your GCP project ID
```

## ⚙️ How the Workflow Works

### Automatic Triggers
The workflow runs when:
- ✅ Code is pushed to `main` or `develop` branches
- ✅ Changes are made to:
  - `Dockerfile`
  - `requirements.txt`
  - Application code (`app.py`, `main.py`)
  - `networksecurity/` folder
- ✅ Pull requests to `main` or `develop` (build only, no push)
- ✅ Manual trigger via GitHub Actions

### What It Does
1. **Checks out** code
2. **Sets up** Docker Buildx
3. **Authenticates** with Google Cloud
4. **Builds** Docker image with caching
5. **Pushes** to GCR with versioned tags
6. **Verifies** image in registry
7. **Scans** for vulnerabilities (optional)
8. **Generates** summary

## 🏗️ Build Workflow Diagram

```
Code Push/Manual Trigger
        ↓
    Checkout Code
        ↓
 Setup Docker Buildx
        ↓
  Authenticate GCS
        ↓
    Build Image
        ↓
   Push to GCR
        ↓
   Verify Upload
        ↓
  Scan for Vulns
        ↓
  Generate Summary
```

## 📦 Image Naming & Tagging

### Image Path
```
gcr.io/[PROJECT_ID]/network-security-model:[TAG]
```

### Tag Formats

| Trigger | Tag Pattern | Example |
|---------|-------------|---------|
| Push to main | `main-[commit_short]-[timestamp]` | `main-a1b2c3d-20260515_143022` |
| Push to develop | `develop-[commit_short]-[timestamp]` | `develop-x9y8z7w-20260515_143022` |
| Manual trigger | Custom input | `v1.0.0`, `prod`, `latest` |
| All pushes | `latest` | Always updated |

### Examples
```
gcr.io/my-project/network-security-model:main-a1b2c3d
gcr.io/my-project/network-security-model:latest
gcr.io/my-project/network-security-model:v1.0.0
```

## 🔍 View & Manage Images

### Via Google Cloud Console
1. Go to **Container Registry**
2. Click **network-security-model**
3. View all tags and metadata

### Via gcloud CLI
```bash
# List all images
gcloud container images list --project=$PROJECT_ID

# List tags for an image
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --limit=10

# View image details
gcloud container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest
```

### Via Docker CLI
```bash
# Pull an image
docker pull gcr.io/$PROJECT_ID/network-security-model:latest

# Run locally
docker run -it gcr.io/$PROJECT_ID/network-security-model:latest
```

## 🚀 Deploy Pushed Images

### Cloud Run
```bash
gcloud run deploy network-security \
  --image gcr.io/$PROJECT_ID/network-security-model:latest \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --allow-unauthenticated
```

### GKE
```bash
# Create deployment
kubectl create deployment network-security \
  --image=gcr.io/$PROJECT_ID/network-security-model:latest

# Or update existing
kubectl set image deployment/network-security \
  app=gcr.io/$PROJECT_ID/network-security-model:latest
```

### Compute Engine
```bash
gcloud compute instances create-with-container ml-server \
  --container-image=gcr.io/$PROJECT_ID/network-security-model:latest \
  --container-port=5000
```

## 📊 Workflow File Structure

```yaml
name: Build and Push Docker Image to GCR

on:
  push:
    branches: [main, develop]
    paths: [Dockerfile, requirements.txt, ...]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:
    inputs:
      tag:
        description: Custom image tag

env:
  GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  GCR_REGISTRY: gcr.io
  IMAGE_NAME: network-security-model

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Docker Buildx
      - Authenticate GCS
      - Configure Docker auth
      - Generate metadata
      - Build Docker image
      - Load to Docker daemon
      - Push to GCR
      - Get image digest
      - Create summary
      - Verify in GCR
      - Scan vulnerabilities
```

## 🛠️ Setup Methods

### Method 1: Manual Setup (Most Control)

Follow [GCR_SETUP_GUIDE.md](./GCR_SETUP_GUIDE.md) step-by-step

### Method 2: Automated with gcloud

```bash
# Complete setup with one script
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions-gcr"

# Enable API
gcloud services enable containerregistry.googleapis.com

# Create service account
gcloud iam service-accounts create $SA_NAME

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create key
gcloud iam service-accounts keys create gcr-key.json \
  --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com

# Add secrets with GitHub CLI
gh secret set GCP_SA_KEY < gcr-key.json
gh secret set GCP_PROJECT_ID -b "$PROJECT_ID"
```

## 🔐 Security Configuration

### Service Account Permissions

Minimal required permissions:
```yaml
roles/storage.admin      # Image storage
roles/container.developer # Container registry access
```

### Best Practices
1. **Rotate keys regularly** - Generate new keys every 90 days
2. **Use Workload Identity** - Better than static keys
3. **Limit scope** - Apply principle of least privilege
4. **Audit access** - Monitor via Cloud Audit Logs
5. **Scan images** - Enable vulnerability scanning

### Workload Identity (Advanced)

For better security without static keys:
```yaml
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account_email: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

## 📚 Documentation Files

- **[GCR_SETUP_GUIDE.md](./GCR_SETUP_GUIDE.md)** - Detailed 5-step setup
- **[GCR_CONFIG_REFERENCE.md](./GCR_CONFIG_REFERENCE.md)** - Quick reference
- **[GCS_WORKFLOW_README.md](./GCS_WORKFLOW_README.md)** - GCS workflow docs

## 🧪 Testing the Workflow

### Manual Trigger
1. Go to **Actions** tab
2. Select **Build and Push Docker Image to GCR**
3. Click **Run workflow**
4. Select branch
5. Optionally enter custom tag
6. Click **Run workflow**

### Automatic Trigger
Push changes to tracked files:
```bash
# Make a change to Dockerfile or code
git add Dockerfile
git commit -m "Update application"
git push origin main
```

### Monitor Build
1. Go to Actions tab
2. Click the running workflow
3. View real-time build logs
4. Check job status

## 🔍 Verify & Troubleshoot

### Verify Image Exists
```bash
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model
```

### View Build Logs
```bash
# In GitHub Actions
1. Actions tab > Workflow > Run
2. Click "build-and-push" job
3. View detailed logs
```

### Check Image Size
```bash
gcloud container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest \
  --format='value(image_summary.image_size_bytes)'
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Authentication failed | Verify `GCP_SA_KEY` is complete JSON |
| Permission denied | Check service account roles with `gcloud projects get-iam-policy` |
| API not enabled | Run `gcloud services enable containerregistry.googleapis.com` |
| Build timeout | Reduce image size or optimize Dockerfile |
| Disk full | Use multi-stage builds to reduce size |

## 📈 Monitoring & Logs

### GitHub Actions Dashboard
- **Location**: Repository > Actions
- **Workflow**: Build and Push Docker Image to GCR
- **Details**: Build logs, push status, verification results
- **Retention**: 90 days

### GCP Audit Logs
- **Location**: Cloud Console > Logs
- **Filter**: `resource.type="gce_container"` AND `protoPayload.methodName="storage.objects.create"`
- **Insight**: All image push operations

### Image Vulnerability Scanning
```bash
# View scan results
gcloud container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest \
  --show-package-vulnerability

# Latest vulnerability data
gcloud beta container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest \
  --format="value(image_summary.vulnerability_counts)"
```

## 🧹 Maintenance

### Clean Up Old Images
```bash
# Delete images older than 30 days
CUTOFF_DATE=$(date -d "30 days ago" +%Y-%m-%d)

gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --filter="timestamp.datetime < $CUTOFF_DATE" \
  --format="get(digest)" | \
  xargs -I {} gcloud container images delete "gcr.io/$PROJECT_ID/network-security-model@{}" --quiet
```

### Set Image Retention Policy
```bash
# Keep only last 10 images
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --sort-by=~timestamp \
  --limit=10 | tail -n +11 | awk '{print $NF}' | \
  xargs -I {} gcloud container images delete {} --quiet
```

## 💰 Cost Optimization

### Storage Costs
- **Free tier**: 500MB storage included per month
- **Pricing**: $0.026 per GB/month after free tier
- **Tips**: Delete old images, use image deduplication

### Bandwidth Costs
- **Pull from same region**: Free
- **Cross-region**: Charged per GB
- **Tip**: Pull from same region as deployed services

### Scanning Costs
- **Automatic**: Included
- **On-demand**: $0.04 per image scanned
- **Tip**: Regularly delete unneeded images

## 📊 Usage Statistics

After setup, track:
- ✅ Build frequency
- ✅ Image size over time
- ✅ Storage usage
- ✅ Vulnerability trends
- ✅ Deployment frequency

## 🎓 Learning Resources

- [Google Container Registry Docs](https://cloud.google.com/container-registry/docs)
- [GitHub Actions Docker Support](https://docs.github.com/en/actions/guides/publishing-docker-images)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)

## ❓ FAQ

**Q: How often does the workflow run?**
A: Automatically when you push changes to tracked files, or manually via Actions tab.

**Q: Can I use a custom tag?**
A: Yes, manual workflow triggers accept a custom tag input.

**Q: How do I delete an image?**
A: Use `gcloud container images delete gcr.io/PROJECT/IMAGE:TAG`

**Q: What if my image is too large?**
A: Use multi-stage Dockerfile, reduce dependencies, add .dockerignore

**Q: Can I use Artifact Registry instead?**
A: Yes, update the workflow to push to `us-central1-docker.pkg.dev/...`

**Q: How do I sign my images?**
A: Consider using [Binary Authorization](https://cloud.google.com/binary-authorization/docs)

## ✅ Setup Checklist

- [ ] Container Registry API enabled
- [ ] Service account created (`github-actions-gcr`)
- [ ] Roles assigned to service account
- [ ] Service account key created (JSON)
- [ ] `GCP_SA_KEY` secret added to GitHub
- [ ] `GCP_PROJECT_ID` secret added to GitHub
- [ ] Workflow file at `.github/workflows/push-to-gcr.yml`
- [ ] Dockerfile in repository root
- [ ] Manual test successful
- [ ] Image appears in GCR

## 🎉 Next Steps

1. **Complete Setup** - Run gcloud commands above
2. **Add Secrets** - Set GitHub repository secrets
3. **Test Build** - Manual trigger from Actions tab
4. **Monitor** - Check workflow logs and GCR
5. **Deploy** - Use image in Cloud Run, GKE, or other services
6. **Automate** - Push changes to trigger workflows

---

**Last Updated:** 2026-05-15
**Workflow Version:** 1.0
**Status:** ✅ Production Ready
