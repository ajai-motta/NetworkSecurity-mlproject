# GCS Upload Workflow - Complete Setup Guide

## 📋 Overview

This workflow automatically uploads your `final_model` folder to Google Cloud Storage (GCS) whenever you push changes, using GitHub repository secrets for secure credential management.

## 🚀 Quick Start

### Step 1: Run Setup Helper (Windows)
```powershell
.\setup-gcs-workflow.ps1
```

### Step 1: Run Setup Helper (Linux/Mac)
```bash
chmod +x setup-gcs-workflow.sh
./setup-gcs-workflow.sh
```

### Step 2: Add GitHub Secrets
See [GCS_SETUP_GUIDE.md](./GCS_SETUP_GUIDE.md) - Section: "Add GitHub Repository Secrets"

### Step 3: Test the Workflow
Push changes or manually trigger from GitHub Actions tab

## 📁 Files Created

| File | Purpose |
|------|---------|
| `.github/workflows/upload-to-gcs.yml` | Main workflow file |
| `GCS_SETUP_GUIDE.md` | Detailed setup instructions |
| `GCS_CONFIG_REFERENCE.md` | Quick reference for configuration |
| `setup-gcs-workflow.sh` | Helper script (Linux/Mac) |
| `setup-gcs-workflow.ps1` | Helper script (Windows) |
| `GCS_WORKFLOW_README.md` | This file |

## 🔑 Required GitHub Secrets

Create these secrets in your GitHub repository (Settings > Secrets and variables > Actions):

```
GCP_SA_KEY          → Contents of service account JSON key file
GCP_PROJECT_ID      → Your GCP project ID
GCS_BUCKET_NAME     → Your GCS bucket name (without gs://)
```

## ⚙️ How the Workflow Works

### Triggers
The workflow runs automatically when:
- ✅ Code is pushed to `main` or `develop` branches
- ✅ Changes are made to `final_model/**` folder
- ✅ Workflow file itself is modified
- ✅ Manual trigger via GitHub Actions (workflow_dispatch)

### What It Does
1. **Checks out** your repository code
2. **Authenticates** with Google Cloud using service account
3. **Creates timestamp** folder (YYYYMMDD_HHMMSS format)
4. **Uploads** `final_model/` contents to GCS
5. **Verifies** upload was successful
6. **Generates** summary in workflow run

### Upload Location
```
gs://[bucket-name]/models/[timestamp]/
```

Example: `gs://my-bucket/models/20260515_143022/`

## 📊 Workflow Diagram

```
Code Push/Manual Trigger
        ↓
    Checkout Code
        ↓
  Authenticate GCS
        ↓
  Create Timestamp
        ↓
  Upload to GCS
        ↓
   Verify Upload
        ↓
   Generate Summary
```

## 🛠️ Setup Methods

### Method 1: Automatic Setup (Recommended)

**Windows:**
```powershell
.\setup-gcs-workflow.ps1
# Choose option 6 (Full automatic setup)
```

**Linux/Mac:**
```bash
./setup-gcs-workflow.sh
# Choose option 7 (Full automatic setup)
```

### Method 2: Manual Setup

Follow [GCS_SETUP_GUIDE.md](./GCS_SETUP_GUIDE.md) step-by-step

### Method 3: GitHub CLI

If you have GitHub CLI installed:
```bash
# Set secrets directly
gh secret set GCP_SA_KEY < service-account-key.json
gh secret set GCP_PROJECT_ID -b "your-project-id"
gh secret set GCS_BUCKET_NAME -b "your-bucket-name"
```

## 📦 Required Tools

- **Google Cloud SDK** - For GCS access
  - Install: https://cloud.google.com/sdk/docs/install
  - Initialize: `gcloud init`
  - Authenticate: `gcloud auth login`

- **GitHub CLI** (optional) - For easier secret setup
  - Install: https://cli.github.com
  - Authenticate: `gh auth login`

- **jq** (optional) - For JSON parsing
  - Linux: `sudo apt-get install jq`
  - Mac: `brew install jq`
  - Windows: `choco install jq`

## 🔐 Security Setup

### Create Service Account
```bash
gcloud iam service-accounts create github-actions-gcs \
  --display-name="GitHub Actions GCS Upload"
```

### Assign Permissions
```bash
# Set project
export PROJECT_ID="your-project-id"
export SA_EMAIL="github-actions-gcs@${PROJECT_ID}.iam.gserviceaccount.com"
export BUCKET_NAME="your-bucket-name"

# Grant bucket access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectCreator"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.objectViewer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.bucketReader"
```

### Generate Key
```bash
gcloud iam service-accounts keys create gcs-key.json \
  --iam-account=$SA_EMAIL
```

## 📝 Usage Examples

### View Uploaded Models
```bash
# List all uploads
gsutil ls -r gs://your-bucket/models/

# List specific date
gsutil ls -r gs://your-bucket/models/20260515*/

# Download specific upload
gsutil -m cp -r gs://your-bucket/models/20260515_143022/ ./downloaded_model/
```

### Monitor Workflow
1. Go to GitHub repository
2. Click **Actions** tab
3. Select **Upload Final Model to GCS**
4. View run logs in real-time

### Manually Trigger
1. Go to **Actions** > **Upload Final Model to GCS**
2. Click **Run workflow**
3. Select branch and click **Run workflow**

## 🐛 Troubleshooting

### "Authentication failed"
**Solution:** Verify `GCP_SA_KEY` contains complete JSON
```bash
# Validate JSON
cat gcs-key.json | jq empty && echo "Valid" || echo "Invalid"
```

### "Permission denied" 
**Solution:** Check service account has bucket roles
```bash
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

### "Bucket not found"
**Solution:** Verify bucket exists and name is correct (no `gs://` prefix)
```bash
gsutil ls -b gs://your-bucket-name
```

### Workflow doesn't trigger
**Solution:** Check file paths in workflow conditions
```yaml
paths:
  - 'final_model/**'  # Matches files in final_model folder
  - '.github/workflows/upload-to-gcs.yml'  # Workflow file itself
```

## 📚 Documentation Files

- **[GCS_SETUP_GUIDE.md](./GCS_SETUP_GUIDE.md)** - Complete setup instructions
- **[GCS_CONFIG_REFERENCE.md](./GCS_CONFIG_REFERENCE.md)** - Configuration reference

## 🔧 Customization

### Change Bucket Structure
Edit `.github/workflows/upload-to-gcs.yml`:
```yaml
# Current structure
gs://${{ secrets.GCS_BUCKET_NAME }}/models/${{ steps.timestamp.outputs.timestamp }}/

# Custom structure example
gs://${{ secrets.GCS_BUCKET_NAME }}/network-security/${{ github.run_number }}/
```

### Change Trigger Branches
```yaml
on:
  push:
    branches:
      - main          # Your production branch
      - develop       # Your development branch
      - staging       # Add more branches as needed
```

### Disable Path Filtering
```yaml
on:
  push:
    branches:
      - main
    # Remove paths to trigger on any push
```

## 📊 Workflow Statistics

After setup, you can track:
- **Upload frequency** - How often models are updated
- **Upload size** - Model folder size over time
- **Success rate** - Workflow reliability
- **Storage costs** - GCS usage tracking

## 🔄 Maintenance

### Weekly Tasks
- [ ] Check workflow runs in GitHub Actions
- [ ] Monitor GCS storage usage
- [ ] Verify uploads are complete

### Monthly Tasks
- [ ] Rotate service account keys (recommended)
- [ ] Review and clean old model versions
- [ ] Update documentation as needed

### Quarterly Tasks
- [ ] Audit GCS permissions
- [ ] Review security settings
- [ ] Update workflow for new features

## 🎓 Learning Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud Storage Guide](https://cloud.google.com/storage/docs)
- [gsutil Tool Reference](https://cloud.google.com/storage/docs/gsutil)
- [Service Accounts Guide](https://cloud.google.com/iam/docs/service-accounts)

## ❓ FAQ

**Q: How often does the workflow run?**
A: Automatically when you push changes to `final_model/` folder, or manually via Actions tab.

**Q: Can I download models from GCS?**
A: Yes, use `gsutil cp` command or download from Google Cloud Console.

**Q: Is my service account key secure?**
A: Yes, GitHub encrypts secrets and you can rotate keys anytime.

**Q: How much does GCS storage cost?**
A: Depends on region and storage class. Check [GCS Pricing](https://cloud.google.com/storage/pricing).

**Q: Can I use Workload Identity instead?**
A: Yes, for better security. See GCS_SETUP_GUIDE.md - "Workload Identity Federation" section.

## 📞 Support

For issues or questions:
1. Check [GCS_SETUP_GUIDE.md](./GCS_SETUP_GUIDE.md) - Troubleshooting section
2. Review workflow logs in GitHub Actions
3. Verify GCS permissions with `gcloud` commands
4. Check Cloud Audit Logs in GCP Console

## ✅ Setup Checklist

- [ ] Google Cloud Project created
- [ ] GCS bucket created with versioning enabled
- [ ] Service account created with permissions
- [ ] Service account key downloaded (JSON)
- [ ] `GCP_SA_KEY` secret added to GitHub
- [ ] `GCP_PROJECT_ID` secret added to GitHub
- [ ] `GCS_BUCKET_NAME` secret added to GitHub
- [ ] Workflow file exists at `.github/workflows/upload-to-gcs.yml`
- [ ] Test workflow via manual trigger
- [ ] Verify upload in GCS bucket
- [ ] Monitor workflow runs in Actions tab

## 🎉 Next Steps

1. **Complete Setup** - Run setup helper script
2. **Test Workflow** - Manually trigger from Actions tab
3. **Monitor Upload** - Check GCS bucket for files
4. **Automate** - Push changes to `final_model/` to trigger workflow
5. **Integrate** - Use uploaded models in deployment pipelines

---

**Last Updated:** 2026-05-15
**Workflow Version:** 1.0
**Status:** ✅ Production Ready
