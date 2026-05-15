# CI/CD Pipeline: Complete Workflow Integration

This document explains how to use both GCS and GCR workflows together to create a complete machine learning CI/CD pipeline.

## 📊 Overview

You now have two automated workflows:

1. **GCR Workflow** - Builds and pushes Docker images to Google Container Registry
2. **GCS Workflow** - Uploads trained models to Google Cloud Storage

## 🔄 Complete Pipeline Flow

```
Code Push (main/develop)
        ↓
    ┌───────────────────┐
    │  GCR Workflow     │
    │  Build Docker     │
    │  Push to GCR      │
    └────────┬──────────┘
             ↓
    Docker Image Ready
         in GCR
         
Model Update Push
        ↓
    ┌───────────────────┐
    │  GCS Workflow     │
    │  Upload Model     │
    │  Push to GCS      │
    └────────┬──────────┘
             ↓
    Model Checkpoint
        in GCS
```

## 📁 Workflow Files Created

```
.github/workflows/
├── push-to-gcr.yml          # Build & push Docker images to GCR
└── upload-to-gcs.yml        # Upload models to GCS

Documentation Files:
├── GCR_WORKFLOW_README.md      # Complete GCR setup guide
├── GCR_SETUP_GUIDE.md          # Detailed GCR configuration
├── GCR_CONFIG_REFERENCE.md     # GCR quick reference
├── GCS_WORKFLOW_README.md      # Complete GCS setup guide
├── GCS_SETUP_GUIDE.md          # Detailed GCS configuration
├── GCS_CONFIG_REFERENCE.md     # GCS quick reference
└── PIPELINE_INTEGRATION.md     # This file

Setup Scripts:
├── setup-gcr-workflow.ps1      # Windows setup for GCR
├── setup-gcr-workflow.sh       # Linux/Mac setup for GCR
├── setup-gcs-workflow.ps1      # Windows setup for GCS
└── setup-gcs-workflow.sh       # Linux/Mac setup for GCS
```

## 🚀 Quick Setup

### Step 1: Setup Both Workflows (Windows)

**For GCR:**
```powershell
.\setup-gcr-workflow.ps1
# Choose option 7 for full automatic setup
```

**For GCS:**
```powershell
.\setup-gcs-workflow.ps1
# Choose option 7 for full automatic setup
```

### Step 1: Setup Both Workflows (Linux/Mac)

**For GCR:**
```bash
chmod +x setup-gcr-workflow.sh
./setup-gcr-workflow.sh
# Choose option 7 for full automatic setup
```

**For GCS:**
```bash
chmod +x setup-gcs-workflow.sh
./setup-gcs-workflow.sh
# Choose option 7 for full automatic setup
```

### Step 2: Verify All Secrets

Go to GitHub repository > Settings > Secrets and variables > Actions

Verify these secrets exist:
- ✅ `GCP_SA_KEY` - Service account JSON key
- ✅ `GCP_PROJECT_ID` - Your GCP project ID
- ✅ `GCS_BUCKET_NAME` - GCS bucket for models

## 🔑 GitHub Secrets Required

| Secret | Used By | Purpose |
|--------|---------|---------|
| `GCP_SA_KEY` | Both | Authentication with Google Cloud |
| `GCP_PROJECT_ID` | Both | GCP project identifier |
| `GCS_BUCKET_NAME` | GCS Only | Model storage bucket |

## 📦 Workflow 1: GCR (Docker Images)

### Triggers
- ✅ Push to `main` or `develop` branches
- ✅ Changes to: `Dockerfile`, `app.py`, `networksecurity/**`
- ✅ Pull requests (build only, no push)
- ✅ Manual trigger with custom tags

### Creates
- Docker image with automatic versioning
- Tags: `branch-commit-timestamp` + `latest`
- Stored in: `gcr.io/[PROJECT_ID]/network-security-model:[TAG]`

### Example
```
gcr.io/my-project/network-security-model:main-a1b2c3d-20260515_143022
gcr.io/my-project/network-security-model:latest
```

### Use Cases
- Deploy to Cloud Run
- Deploy to GKE
- Deploy to Compute Engine
- Use in CI/CD pipelines

## 📊 Workflow 2: GCS (Models)

### Triggers
- ✅ Push to `main` or `develop` branches
- ✅ Changes to: `final_model/**`
- ✅ Workflow file changes
- ✅ Manual trigger (workflow_dispatch)

### Creates
- Timestamped model folder in GCS
- Path: `gs://[BUCKET]/models/[YYYYMMDD_HHMMSS]/`
- Includes all model files

### Example
```
gs://my-bucket/models/20260515_143022/
  ├── model_weights.pkl
  ├── model_config.json
  └── ...
```

### Use Cases
- Model versioning and history
- Model serving setup
- Backup and recovery
- Model analysis and comparison

## 🔗 Integration Scenarios

### Scenario 1: Update Code Only

```
git push origin main
    ↓
GCR Workflow Triggers
    ↓
New Docker image built
    ↓
Pushed to: gcr.io/project/image:main-xxx
    ↓
GCS Workflow: No change (final_model unchanged)
```

### Scenario 2: Train New Model

```
git add final_model/
git commit -m "New model weights"
git push origin main
    ↓
GCR Workflow Triggers (if code changed)
    ↓
GCS Workflow Triggers (final_model changed)
    ↓
Both workflows run in parallel
    ↓
New Docker image in GCR
+ Model checkpoint in GCS
```

### Scenario 3: Manual Model Upload

```
GitHub Actions > Upload Final Model to GCS
    ↓
Manual trigger workflow_dispatch
    ↓
Model uploaded with custom timestamp
    ↓
gs://bucket/models/20260515_143022/
```

## 📈 Monitoring Workflows

### View Workflow Runs
1. Go to GitHub repository
2. Click **Actions** tab
3. See all workflow runs

### View Specific Workflow
**GCR Builds:**
- Actions > Build and Push Docker Image to GCR
- Shows image tags and push status

**GCS Uploads:**
- Actions > Upload Final Model to GCS
- Shows upload path and verification status

### Access Artifacts

**Docker Images in GCR:**
```bash
gcloud container images list --project=$PROJECT_ID
gcloud container images list-tags gcr.io/$PROJECT_ID/network-security-model
```

**Models in GCS:**
```bash
gsutil ls -r gs://your-bucket/models/
gsutil ls -r gs://your-bucket/models/20260515_*/
```

## 🛠️ Advanced Configuration

### Customize GCR Triggers

Edit `.github/workflows/push-to-gcr.yml`:

```yaml
on:
  push:
    branches:
      - main
      - develop
      - staging          # Add branches
    paths:
      - 'Dockerfile'
      - 'requirements.txt'
      - 'app.py'
      - 'new_folder/**'   # Add paths
```

### Customize GCS Triggers

Edit `.github/workflows/upload-to-gcs.yml`:

```yaml
on:
  push:
    branches:
      - main
      - develop
    paths:
      - 'final_model/**'  # Change as needed
```

### Disable Workflows

To disable a workflow temporarily:
1. Go to Actions tab
2. Click the workflow name
3. Click "..." menu
4. Select "Disable workflow"

## 🔐 Security Configuration

### Service Account Setup

You may need 1 or 2 service accounts:

**Option 1: Shared Service Account (Simpler)**
```bash
# Create one account with both permissions
gcloud iam service-accounts create github-actions-ml \
  --display-name="GitHub Actions ML Pipeline"

# Grant both permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/storage.admin"          # For GCS

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:sa@project.iam.gserviceaccount.com" \
  --role="roles/container.developer"    # For GCR
```

**Option 2: Separate Service Accounts (More Secure)**
```bash
# Create GCR service account
gcloud iam service-accounts create github-actions-gcr

# Create GCS service account  
gcloud iam service-accounts create github-actions-gcs

# Grant specific permissions to each
# (see individual setup guides)
```

### Key Rotation

Rotate keys every 90 days:
```bash
# List keys
gcloud iam service-accounts keys list \
  --iam-account=sa@project.iam.gserviceaccount.com

# Delete old key (keep one active)
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=sa@project.iam.gserviceaccount.com

# Create new key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=sa@project.iam.gserviceaccount.com

# Update GitHub secret
gh secret set GCP_SA_KEY < new-key.json
```

## 📊 Workflow Statistics

Track these metrics over time:

### GCR Metrics
- Build frequency (changes per week)
- Build success rate (%)
- Average build time (minutes)
- Image size (MB)
- Tag count

### GCS Metrics
- Upload frequency (changes per week)
- Model file count
- Total storage used (GB)
- Oldest model retention

## 🧹 Maintenance

### Weekly
- [ ] Check workflow success rates
- [ ] Review recent images and models
- [ ] Monitor storage usage

### Monthly
- [ ] Clean up old images (> 30 days)
- [ ] Archive old models
- [ ] Review logs for errors

### Quarterly
- [ ] Audit permissions
- [ ] Rotate service account keys
- [ ] Update documentation

## 🐛 Troubleshooting

### Both Workflows Fail

1. **Check secrets:**
   ```bash
   # Verify secrets exist
   gh secret list | grep GCP
   ```

2. **Check permissions:**
   ```bash
   gcloud projects get-iam-policy $PROJECT_ID
   ```

3. **Check APIs enabled:**
   ```bash
   gcloud services list --enabled | grep -E "container|storage"
   ```

### GCR Workflow Fails

- Verify `Dockerfile` exists in repo root
- Check Docker image size (< 4GB typical)
- Review build logs for syntax errors

### GCS Workflow Fails

- Verify `final_model/` folder exists
- Check folder has files to upload
- Verify bucket exists and is accessible

### Workflows Don't Trigger

- Verify branch names match (`main`, `develop`)
- Check file paths in triggers
- Ensure files are actually changed

## 📚 Documentation Guide

| Document | Purpose | Audience |
|----------|---------|----------|
| GCR_WORKFLOW_README.md | Complete GCR guide | Everyone |
| GCR_SETUP_GUIDE.md | Detailed setup steps | First-time setup |
| GCR_CONFIG_REFERENCE.md | Quick lookup | Configuration |
| GCS_WORKFLOW_README.md | Complete GCS guide | Everyone |
| GCS_SETUP_GUIDE.md | Detailed setup steps | First-time setup |
| GCS_CONFIG_REFERENCE.md | Quick lookup | Configuration |
| PIPELINE_INTEGRATION.md | This file | Using both together |

## 🚀 Next Steps

1. **Setup GCR** - Run `setup-gcr-workflow.ps1` or `setup-gcr-workflow.sh`
2. **Setup GCS** - Run `setup-gcs-workflow.ps1` or `setup-gcs-workflow.sh`
3. **Test GCR** - Push code change to trigger first image build
4. **Test GCS** - Update `final_model/` and push to trigger model upload
5. **Monitor** - Check Actions tab for both workflows
6. **Deploy** - Use Docker images and models in your deployment

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Container Registry](https://cloud.google.com/container-registry/docs)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [ML Deployment Guide](https://cloud.google.com/ai-platform/docs)

## ❓ FAQ

**Q: Can I use the same service account for both workflows?**
A: Yes! Create one service account with both `storage.admin` and `container.developer` roles.

**Q: What if I only need one workflow?**
A: You can delete the other workflow file. Both are independent.

**Q: How do I trigger workflows manually?**
A: Use workflow_dispatch feature in Actions tab.

**Q: Can I modify the image/model paths?**
A: Yes! Edit the workflow files to customize paths and names.

**Q: How often do workflows run?**
A: Automatically on push to tracked branches/paths, or manually on demand.

**Q: What are the costs?**
A: GitHub Actions minutes (free for public repos), GCR storage ($0.026/GB/month), GCS storage ($0.020/GB/month).

## 📞 Support

For issues:
1. Check relevant documentation (GCR_SETUP_GUIDE.md or GCS_SETUP_GUIDE.md)
2. Review workflow logs in GitHub Actions tab
3. Verify secrets and permissions
4. Check GCP Cloud Audit Logs
5. Test manually with gcloud and gsutil commands

## ✅ Complete Setup Checklist

### GCR Setup
- [ ] Container Registry API enabled
- [ ] Service account created
- [ ] Roles assigned
- [ ] Key created and downloaded
- [ ] GCP_SA_KEY secret added
- [ ] GCP_PROJECT_ID secret added
- [ ] Workflow file present

### GCS Setup
- [ ] GCS bucket created
- [ ] Service account created
- [ ] Roles assigned
- [ ] Key created and downloaded
- [ ] GCP_SA_KEY secret added
- [ ] GCP_PROJECT_ID secret added
- [ ] GCS_BUCKET_NAME secret added
- [ ] Workflow file present

### Testing
- [ ] GCR: Pushed code, image created
- [ ] GCS: Updated model, files uploaded
- [ ] Both workflows logged successfully

---

**Last Updated:** 2026-05-15
**Pipeline Version:** 1.0
**Status:** ✅ Production Ready
