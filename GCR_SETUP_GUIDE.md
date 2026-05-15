# Docker Image to GCR Setup Guide

This guide explains how to configure the GitHub Actions workflow to automatically build and push Docker images to Google Container Registry (GCR).

## Prerequisites

1. **Google Cloud Project** - Create a project at [Google Cloud Console](https://console.cloud.google.com)
2. **Container Registry enabled** - Enable GCR API in your GCP project
3. **Service Account** - Create a service account with container registry permissions
4. **GitHub Repository** - Push code to GitHub to enable Actions

## Step-by-Step Setup

### 1. Enable Container Registry API

**Via Google Cloud Console:**
1. Go to **APIs & Services** > **Library**
2. Search for "Container Registry API"
3. Click **Enable**

**Via gcloud CLI:**
```bash
gcloud services enable containerregistry.googleapis.com
```

### 2. Create a Service Account with GCR Permissions

**Via Google Cloud Console:**
1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Enter a name (e.g., `github-actions-gcr`)
4. Grant the following roles:
   - `roles/storage.admin` - Storage access for image storage
   - `roles/container.developer` - Container registry access
   - `roles/viewer` - For querying images

**Or use gcloud:**
```bash
# Set variables
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions-gcr"

# Create service account
gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions Container Registry"

# Grant roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"
```

### 3. Generate and Download Service Account Key

1. Click on the service account you created
2. Go to **Keys** tab
3. Click **Add Key** > **Create new key**
4. Choose **JSON** format
5. Download the key file

**Or use gcloud:**
```bash
gcloud iam service-accounts keys create gcr-key.json \
  --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

### 4. Add GitHub Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** and add:

| Secret Name | Value |
|---|---|
| `GCP_SA_KEY` | Contents of the JSON key file (entire JSON) |
| `GCP_PROJECT_ID` | Your GCP project ID |

### 5. Verify Setup

Test the workflow by:
1. Going to **Actions** > **Build and Push Docker Image to GCR**
2. Click **Run workflow**
3. Select your branch and click **Run workflow**

## Workflow Behavior

### Automatic Triggers

The workflow runs when:
- Code is pushed to `main` or `develop` branches
- Changes are made to:
  - `Dockerfile`
  - `requirements.txt`
  - `app.py` / `main.py`
  - `networksecurity/` folder
  - `.github/workflows/push-to-gcr.yml`
- Pull requests to `main` or `develop` (build only, no push)
- Manual trigger via **Actions** tab (workflow_dispatch)

### What the Workflow Does

1. ✅ Checks out your repository
2. ✅ Sets up Docker Buildx for advanced builds
3. ✅ Authenticates with Google Cloud
4. ✅ Configures Docker authentication for GCR
5. ✅ Builds Docker image with caching
6. ✅ Pushes image to GCR with multiple tags
7. ✅ Verifies image in registry
8. ✅ Scans image for vulnerabilities (optional)
9. ✅ Generates summary in workflow run

## Image Naming and Tagging

### Tag Format

```
gcr.io/[PROJECT_ID]/network-security-model:[TAG]
```

### Tag Examples

| Scenario | Tag Format | Example |
|----------|-----------|---------|
| Push to main | `main-[commit_sha:7]-[timestamp]` | `main-a1b2c3d-20260515_143022` |
| Push to develop | `develop-[commit_sha:7]-[timestamp]` | `develop-x9y8z7w-20260515_143022` |
| Manual trigger | Custom tag from input | `v1.0.0`, `latest`, `prod` |
| Automatic latest | `latest` | Always pushed for latest |

### Accessing Images

**View in Google Cloud Console:**
1. Go to **Container Registry** > **network-security-model**
2. See all tags and metadata

**Via gcloud CLI:**
```bash
# List all images
gcloud container images list --project=$PROJECT_ID

# List all tags for an image
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --project=$PROJECT_ID

# Pull an image
docker pull gcr.io/$PROJECT_ID/network-security-model:main-a1b2c3d
```

## Using Pushed Images

### Run in Cloud Run

```bash
gcloud run deploy network-security-api \
  --image gcr.io/$PROJECT_ID/network-security-model:latest \
  --platform managed \
  --region us-central1
```

### Run in GKE

```bash
kubectl create deployment network-security \
  --image=gcr.io/$PROJECT_ID/network-security-model:latest
```

### Pull Locally

```bash
docker pull gcr.io/$PROJECT_ID/network-security-model:latest
docker run -it gcr.io/$PROJECT_ID/network-security-model:latest
```

## Environment Variables in Workflow

The workflow uses these from secrets:

```yaml
GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
GCR_REGISTRY: gcr.io
IMAGE_NAME: network-security-model
```

## Workflow Customization

### Change Image Name

Edit `.github/workflows/push-to-gcr.yml`:
```yaml
env:
  IMAGE_NAME: your-custom-image-name
```

### Change Trigger Branches

```yaml
on:
  push:
    branches:
      - main
      - develop
      - staging  # Add more branches
```

### Change Trigger Paths

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'Dockerfile'
      - 'requirements.txt'
      - 'app.py'
      - 'networksecurity/**'
```

### Disable on PR

Remove or modify pull_request section:
```yaml
# Remove this section to disable PR builds
# pull_request:
#   branches:
#     - main
#     - develop
```

## Image Vulnerability Scanning

The workflow includes optional vulnerability scanning. To view scan results:

```bash
gcloud container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest \
  --show-package-vulnerability
```

## Troubleshooting

### Authentication Error

**Error:** `Failed to authenticate`

**Solution:** Verify GCP_SA_KEY secret contains complete JSON:
```bash
cat gcr-key.json | jq empty && echo "Valid JSON" || echo "Invalid JSON"
```

### Permission Denied

**Error:** `Permission 'storage.buckets.create' denied`

**Solution:** Ensure service account has correct roles:
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

### Container Registry API Not Enabled

**Error:** `API containerregistry.googleapis.com not enabled`

**Solution:** Enable the API:
```bash
gcloud services enable containerregistry.googleapis.com
```

### Dockerfile Not Found

**Error:** `COPY failed: file not found`

**Solution:** Ensure Dockerfile is in repository root and committed

### Image Too Large

**Error:** `Requested entity too large`

**Solution:**
- Reduce Dockerfile size
- Use multi-stage builds
- Remove unnecessary files
- Add .dockerignore

### Build Timeout

**Error:** `Build canceled due to timeout`

**Solution:**
- Optimize Docker layers
- Cache dependencies
- Use BuildKit caching
- Split into smaller images

## Security Best Practices

1. **Rotate Keys Regularly** - Generate new service account keys periodically
2. **Use Workload Identity** - Consider [Workload Identity Federation](https://cloud.google.com/docs/authentication/workload-identity-federation)
3. **Limit Permissions** - Use least privilege principle
4. **Scan Images** - Enable vulnerability scanning
5. **Use Image Signing** - Consider signing images for verification
6. **Audit Access** - Monitor GCR access logs

## Advanced Configuration

### Multi-Stage Build

Optimize your Dockerfile:

```dockerfile
# Build stage
FROM python:3.9 as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "app.py"]
```

### Using Workload Identity Federation

For enhanced security without static keys:

```yaml
- name: Authenticate to Google Cloud (Workload Identity)
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
    service_account_email: ${{ secrets.WIF_SERVICE_ACCOUNT }}
```

### Push to Multiple Registries

Add Docker Hub or Artifact Registry:

```yaml
- name: Push to multiple registries
  run: |
    # GCR
    docker push gcr.io/$PROJECT_ID/image:tag
    
    # Artifact Registry
    docker push us-central1-docker.pkg.dev/$PROJECT_ID/repo/image:tag
```

## Monitoring and Logging

### GitHub Actions Logs
- **Location**: Repository > Actions tab
- **Search**: "Build and Push Docker Image to GCR"
- **Retention**: 90 days default

### GCP Logs
- **Location**: Cloud Console > Logs
- **Filter**: `resource.type="gce_container"` AND `protoPayload.methodName="storage.buckets.get"`

## Image Cleanup

Remove old images to save costs:

```bash
# Delete old image tags (keep last 5)
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --sort-by=~timestamp \
  --limit=10 | tail -n +6 | awk '{print $NF}' | \
  xargs -I {} gcloud container images delete {} --quiet
```

## Additional Resources

- [Google Container Registry Documentation](https://cloud.google.com/container-registry/docs)
- [GitHub Actions Docker Build Documentation](https://github.com/docker/build-push-action)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GCR Pricing](https://cloud.google.com/container-registry/pricing)

## Questions or Issues?

For troubleshooting:
1. Check GitHub Actions workflow logs
2. Review GCP Cloud Audit Logs
3. Verify all secrets are set correctly
4. Test manually with Docker and gcloud commands
