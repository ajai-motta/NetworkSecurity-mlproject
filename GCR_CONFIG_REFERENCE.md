# GCR Push Configuration Reference

## Quick Setup Commands

### 1. Enable Container Registry API
```bash
gcloud services enable containerregistry.googleapis.com
```

### 2. Create Service Account
```bash
export PROJECT_ID="your-project-id"
export SA_NAME="github-actions-gcr"

gcloud iam service-accounts create $SA_NAME \
  --display-name="GitHub Actions GCR"
```

### 3. Grant Required Roles
```bash
# Grant storage admin (for image storage)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Grant container developer
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"
```

### 4. Create and Download Key
```bash
gcloud iam service-accounts keys create gcr-key.json \
  --iam-account=$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

### 5. Add GitHub Secrets
```bash
# Display key for copying
cat gcr-key.json

# Or use GitHub CLI
gh secret set GCP_SA_KEY < gcr-key.json
gh secret set GCP_PROJECT_ID -b "your-project-id"
```

## GitHub Secrets Configuration

### Secret Values Reference

```
GCP_SA_KEY: [Entire JSON content of service account key]
GCP_PROJECT_ID: [Project ID from GCP Console]
```

### Example Values
```
GCP_PROJECT_ID=my-project-123456
GCR_REGISTRY=gcr.io
IMAGE_NAME=network-security-model
```

## Workflow File Locations

```
.github/
└── workflows/
    ├── upload-to-gcs.yml          (Model storage)
    └── push-to-gcr.yml            (Docker images)
```

## Image Registry Paths

| Registry | Path Format | Example |
|----------|-------------|---------|
| GCR | `gcr.io/[PROJECT]/[IMAGE]:[TAG]` | `gcr.io/my-project/network-security-model:latest` |
| Artifact Registry | `[REGION]-docker.pkg.dev/[PROJECT]/[REPO]/[IMAGE]:[TAG]` | `us-central1-docker.pkg.dev/my-project/repo/image:latest` |

## Workflow Triggers

| Event | Condition | When |
|-------|-----------|------|
| Push to main | Changes in paths | Automatic ✅ |
| Push to develop | Changes in paths | Automatic ✅ |
| Pull request | Changes in paths | Build only ⚙️ |
| Manual dispatch | GitHub Actions tab | Manual 🎛️ |

## Image Tag Patterns

```
main-[commit_sha:7]-[timestamp]        → main-a1b2c3d-20260515_143022
develop-[commit_sha:7]-[timestamp]     → develop-x9y8z7w-20260515_143022
latest                                  → Always pushed
custom-tag (manual)                     → v1.0.0, prod, staging
```

## Trigger Paths

Workflow runs when these files change:
```yaml
paths:
  - 'Dockerfile'
  - 'requirements.txt'
  - 'app.py'
  - 'main.py'
  - 'networksecurity/**'
  - '.github/workflows/push-to-gcr.yml'
```

## Permissions Matrix

| Role | Permissions | Required |
|---|---|---|
| `roles/storage.admin` | Create, update, delete buckets/objects | ✅ Yes |
| `roles/container.developer` | Read/write container images | ✅ Yes |
| `roles/viewer` | Query resources (read-only) | ✅ Yes |
| `roles/container.admin` | Full container management | ❌ No |

## Common gcloud Commands

### List Images
```bash
# All images in project
gcloud container images list --project=$PROJECT_ID

# All tags for an image
gcloud container images list-tags \
  gcr.io/$PROJECT_ID/network-security-model \
  --limit=10
```

### Pull Image
```bash
docker pull gcr.io/$PROJECT_ID/network-security-model:latest
```

### Delete Image
```bash
gcloud container images delete \
  gcr.io/$PROJECT_ID/network-security-model:old-tag
```

### Scan for Vulnerabilities
```bash
gcloud container images scan \
  gcr.io/$PROJECT_ID/network-security-model:latest
```

### View Image Details
```bash
gcloud container images describe \
  gcr.io/$PROJECT_ID/network-security-model:latest
```

## Image Usage Examples

### Run with Docker
```bash
docker run -p 5000:5000 \
  gcr.io/$PROJECT_ID/network-security-model:latest
```

### Deploy to Cloud Run
```bash
gcloud run deploy network-security \
  --image gcr.io/$PROJECT_ID/network-security-model:latest \
  --platform managed \
  --region us-central1
```

### Deploy to GKE
```bash
kubectl set image deployment/network-security \
  app=gcr.io/$PROJECT_ID/network-security-model:latest
```

## Monitoring & Logs

### GitHub Actions Logs
- **Location**: Repository > Actions > Build and Push Docker Image to GCR
- **Details**: Shows build steps, push status, verification results
- **Retention**: 90 days default

### GCP Audit Logs
- **Location**: Cloud Console > Logs > Cloud Audit Logs
- **Filter**: `resource.type="gce_container"`
- **Query**: Check `protoPayload.methodName` for image operations

## Common Issues & Solutions

### Issue: "Authentication failed"
**Solution**: Verify JSON key in `GCP_SA_KEY` is complete
```bash
cat gcr-key.json | jq empty && echo "Valid" || echo "Invalid"
```

### Issue: "Permission denied on resource"
**Solution**: Check service account roles
```bash
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"
```

### Issue: "API containerregistry.googleapis.com not enabled"
**Solution**: Enable the API
```bash
gcloud services enable containerregistry.googleapis.com
```

### Issue: "Dockerfile not found"
**Solution**: Verify Dockerfile is in repo root and committed

### Issue: "Build timeout or disk full"
**Solution**: 
- Reduce Dockerfile size
- Use multi-stage builds
- Use .dockerignore to exclude files

## Configuration Checklist

- [ ] Container Registry API enabled
- [ ] Service account created
- [ ] Service account assigned roles
- [ ] Service account key downloaded (JSON)
- [ ] `GCP_SA_KEY` secret added to GitHub
- [ ] `GCP_PROJECT_ID` secret added to GitHub
- [ ] Workflow file exists at `.github/workflows/push-to-gcr.yml`
- [ ] Dockerfile updated if needed
- [ ] Test run via workflow_dispatch
- [ ] Image verified in GCR

## Next Steps

1. **Set up secrets** - Follow GCR_SETUP_GUIDE.md step-by-step
2. **Test workflow** - Manually trigger from Actions tab
3. **Monitor build** - Check workflow logs and GCR
4. **Automate** - Push changes to trigger automatically
5. **Deploy** - Use image in Cloud Run, GKE, or other services

## Support & Documentation

- [GCR_SETUP_GUIDE.md](./GCR_SETUP_GUIDE.md) - Detailed setup instructions
- [Google Container Registry Docs](https://cloud.google.com/container-registry/docs)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [gcloud Container Commands](https://cloud.google.com/sdk/gcloud/reference/container)
