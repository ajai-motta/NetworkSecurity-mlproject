#!/bin/bash
# GCS Upload Workflow Setup Helper
# This script helps configure GitHub secrets for GCS uploads

set -e

echo "======================================"
echo "GCS Upload Workflow Setup Helper"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    if ! command -v gsutil &> /dev/null; then
        echo -e "${RED}❌ gsutil not found. Install Google Cloud SDK first.${NC}"
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq not found. Some features may be limited.${NC}"
        echo "Install: sudo apt-get install jq  (Linux/Mac: brew install jq)"
    fi
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI not found. You'll need to add secrets manually.${NC}"
        echo "Install: https://cli.github.com"
    fi
    
    echo -e "${GREEN}✓ Prerequisites check complete${NC}"
    echo ""
}

# Extract project ID from service account key
extract_project_id() {
    local key_file=$1
    cat "$key_file" | jq -r '.project_id' 2>/dev/null || echo ""
}

# Validate JSON key file
validate_key_file() {
    local key_file=$1
    if [ ! -f "$key_file" ]; then
        echo -e "${RED}❌ File not found: $key_file${NC}"
        return 1
    fi
    
    if ! jq empty "$key_file" 2>/dev/null; then
        echo -e "${RED}❌ Invalid JSON format in: $key_file${NC}"
        return 1
    fi
    
    # Check required fields
    local required_fields=("type" "project_id" "private_key" "client_email")
    for field in "${required_fields[@]}"; do
        if ! jq -e ".$field" "$key_file" > /dev/null 2>&1; then
            echo -e "${RED}❌ Missing required field: $field${NC}"
            return 1
        fi
    done
    
    return 0
}

# List GCS buckets
list_buckets() {
    echo "Available GCS Buckets:"
    echo "====================="
    gsutil ls 2>/dev/null || echo "No buckets found or authentication failed"
    echo ""
}

# Create new bucket
create_bucket() {
    local bucket_name=$1
    local region=${2:-us-central1}
    
    echo "Creating bucket: gs://$bucket_name in $region"
    gsutil mb -l "$region" "gs://$bucket_name"
    
    echo "Enabling versioning..."
    gsutil versioning set on "gs://$bucket_name"
    
    echo -e "${GREEN}✓ Bucket created and versioning enabled${NC}"
}

# Show GitHub CLI setup instructions
show_gh_cli_setup() {
    local gcp_sa_key=$1
    local project_id=$2
    local bucket_name=$3
    
    echo ""
    echo "======================================"
    echo "GitHub CLI Secret Setup"
    echo "======================================"
    echo ""
    echo "Running with GitHub CLI..."
    echo ""
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}GitHub CLI not installed. Manual setup required:${NC}"
        return 1
    fi
    
    # Check GitHub CLI authentication
    if ! gh auth status > /dev/null 2>&1; then
        echo "GitHub CLI not authenticated. Run: gh auth login"
        return 1
    fi
    
    echo "Setting secrets in your GitHub repository..."
    
    # Add secrets
    gh secret set GCP_SA_KEY < "$gcp_sa_key" && \
        echo -e "${GREEN}✓ GCP_SA_KEY secret added${NC}" || \
        echo -e "${RED}❌ Failed to add GCP_SA_KEY${NC}"
    
    echo "$project_id" | gh secret set GCP_PROJECT_ID && \
        echo -e "${GREEN}✓ GCP_PROJECT_ID secret added${NC}" || \
        echo -e "${RED}❌ Failed to add GCP_PROJECT_ID${NC}"
    
    echo "$bucket_name" | gh secret set GCS_BUCKET_NAME && \
        echo -e "${GREEN}✓ GCS_BUCKET_NAME secret added${NC}" || \
        echo -e "${RED}❌ Failed to add GCS_BUCKET_NAME${NC}"
    
    echo ""
    echo "Verifying secrets..."
    gh secret list | grep -E "GCP_SA_KEY|GCP_PROJECT_ID|GCS_BUCKET_NAME" || \
        echo -e "${YELLOW}Could not verify secrets${NC}"
}

# Show manual setup instructions
show_manual_setup() {
    local gcp_sa_key=$1
    local project_id=$2
    local bucket_name=$3
    
    echo ""
    echo "======================================"
    echo "Manual GitHub Secret Setup"
    echo "======================================"
    echo ""
    echo "1. Go to your GitHub repository"
    echo "2. Settings > Secrets and variables > Actions"
    echo "3. Click 'New repository secret'"
    echo ""
    echo "Add the following secrets:"
    echo ""
    
    echo "Secret 1: GCP_SA_KEY"
    echo "Value: (Contents of your service account JSON key file)"
    echo "Path: $gcp_sa_key"
    echo ""
    
    echo "Secret 2: GCP_PROJECT_ID"
    echo "Value: $project_id"
    echo ""
    
    echo "Secret 3: GCS_BUCKET_NAME"
    echo "Value: $bucket_name"
    echo ""
    
    echo -e "${YELLOW}Action Required:${NC}"
    echo "Please add these secrets manually at:"
    echo "https://github.com/[YOUR_ORG]/[YOUR_REPO]/settings/secrets/actions"
}

# Main menu
show_menu() {
    echo "======================================"
    echo "Setup Options"
    echo "======================================"
    echo "1. Check prerequisites"
    echo "2. List existing GCS buckets"
    echo "3. Create new GCS bucket"
    echo "4. Validate service account key file"
    echo "5. Set up GitHub secrets (requires gh CLI)"
    echo "6. Show manual setup instructions"
    echo "7. Full automatic setup"
    echo "0. Exit"
    echo ""
    read -p "Select option (0-7): " option
}

# Full automatic setup
full_setup() {
    echo ""
    echo "======================================"
    echo "Full Automatic Setup"
    echo "======================================"
    echo ""
    
    read -p "Path to service account JSON key file: " key_file
    
    if ! validate_key_file "$key_file"; then
        return 1
    fi
    
    local project_id=$(extract_project_id "$key_file")
    echo -e "${GREEN}✓ Project ID: $project_id${NC}"
    
    echo ""
    list_buckets
    
    read -p "Enter GCS bucket name (or press Enter to create new): " bucket_name
    
    if [ -z "$bucket_name" ]; then
        read -p "New bucket name: " bucket_name
        read -p "Region (default: us-central1): " region
        region=${region:-us-central1}
        create_bucket "$bucket_name" "$region"
    fi
    
    echo ""
    
    # Determine which setup method to use
    if command -v gh &> /dev/null && gh auth status > /dev/null 2>&1; then
        echo "GitHub CLI detected. Use it to set secrets? (y/n): "
        read use_gh
        if [ "$use_gh" = "y" ]; then
            show_gh_cli_setup "$key_file" "$project_id" "$bucket_name"
        else
            show_manual_setup "$key_file" "$project_id" "$bucket_name"
        fi
    else
        show_manual_setup "$key_file" "$project_id" "$bucket_name"
    fi
    
    echo ""
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Verify secrets are in GitHub Settings"
    echo "2. Push changes to trigger the workflow: git push"
    echo "3. Monitor in GitHub Actions tab"
    echo "4. Verify upload with: gsutil ls -r gs://$bucket_name/models/"
}

# Main loop
check_prerequisites

while true; do
    show_menu
    
    case $option in
        1)
            check_prerequisites
            ;;
        2)
            list_buckets
            ;;
        3)
            read -p "Bucket name: " bucket_name
            read -p "Region (default: us-central1): " region
            region=${region:-us-central1}
            create_bucket "$bucket_name" "$region"
            ;;
        4)
            read -p "Path to service account JSON key: " key_file
            if validate_key_file "$key_file"; then
                echo -e "${GREEN}✓ Key file is valid${NC}"
                echo "Project ID: $(extract_project_id "$key_file")"
            fi
            ;;
        5)
            read -p "Path to service account JSON key: " key_file
            if validate_key_file "$key_file"; then
                read -p "GCS bucket name: " bucket_name
                show_gh_cli_setup "$key_file" "$(extract_project_id "$key_file")" "$bucket_name"
            fi
            ;;
        6)
            read -p "Path to service account JSON key: " key_file
            if validate_key_file "$key_file"; then
                read -p "GCS bucket name: " bucket_name
                show_manual_setup "$key_file" "$(extract_project_id "$key_file")" "$bucket_name"
            fi
            ;;
        7)
            full_setup
            ;;
        0)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
