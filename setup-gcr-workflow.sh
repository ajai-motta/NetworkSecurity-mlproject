#!/bin/bash
# GCR Push Workflow Setup Helper
# This script helps configure GitHub secrets for GCR uploads

set -e

echo "======================================"
echo "GCR Push Workflow Setup Helper"
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
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud not found. Install Google Cloud SDK first.${NC}"
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}⚠️  Docker not found (optional but recommended).${NC}"
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  jq not found. Some features may be limited.${NC}"
        echo "Install: sudo apt-get install jq  (Mac: brew install jq)"
    fi
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}⚠️  GitHub CLI not found. You'll need to add secrets manually.${NC}"
        echo "Install: https://cli.github.com"
    fi
    
    echo -e "${GREEN}✓ Prerequisites check complete${NC}"
    echo ""
}

# Enable Container Registry API
enable_cr_api() {
    local project_id=$1
    
    echo "Enabling Container Registry API for project: $project_id"
    
    gcloud services enable containerregistry.googleapis.com --project=$project_id && \
        echo -e "${GREEN}✓ Container Registry API enabled${NC}" || \
        echo -e "${RED}❌ Failed to enable API${NC}"
}

# Create service account
create_service_account() {
    local project_id=$1
    local sa_name=$2
    
    echo "Creating service account: $sa_name"
    
    gcloud iam service-accounts create $sa_name \
        --display-name="GitHub Actions Container Registry" \
        --project=$project_id && \
        echo -e "${GREEN}✓ Service account created${NC}" || \
        echo -e "${YELLOW}⚠️  Service account may already exist${NC}"
}

# Grant service account roles
grant_sa_roles() {
    local project_id=$1
    local sa_name=$2
    
    local sa_email="$sa_name@$project_id.iam.gserviceaccount.com"
    
    echo "Granting roles to service account..."
    
    # Grant storage admin
    gcloud projects add-iam-policy-binding $project_id \
        --member="serviceAccount:$sa_email" \
        --role="roles/storage.admin" \
        --quiet && \
        echo -e "${GREEN}✓ Storage Admin role granted${NC}" || \
        echo -e "${RED}❌ Failed to grant Storage Admin role${NC}"
    
    # Grant container developer
    gcloud projects add-iam-policy-binding $project_id \
        --member="serviceAccount:$sa_email" \
        --role="roles/container.developer" \
        --quiet && \
        echo -e "${GREEN}✓ Container Developer role granted${NC}" || \
        echo -e "${RED}❌ Failed to grant Container Developer role${NC}"
}

# Create service account key
create_sa_key() {
    local project_id=$1
    local sa_name=$2
    local output_file=$3
    
    local sa_email="$sa_name@$project_id.iam.gserviceaccount.com"
    
    echo "Creating service account key: $output_file"
    
    gcloud iam service-accounts keys create $output_file \
        --iam-account=$sa_email \
        --project=$project_id && \
        echo -e "${GREEN}✓ Service account key created${NC}" || \
        echo -e "${RED}❌ Failed to create key${NC}"
}

# Show manual setup instructions
show_manual_setup() {
    local key_file=$1
    local project_id=$2
    
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
    echo "Path: $key_file"
    echo ""
    echo "To copy the content:"
    echo "  cat $key_file | pbcopy  (Mac)"
    echo "  cat $key_file | xclip -selection clipboard  (Linux)"
    echo ""
    
    echo "Secret 2: GCP_PROJECT_ID"
    echo "Value: $project_id"
    echo ""
    
    echo -e "${YELLOW}Action Required:${NC}"
    echo "Please add these secrets manually at:"
    echo "https://github.com/[YOUR_ORG]/[YOUR_REPO]/settings/secrets/actions"
}

# Show GitHub CLI setup
show_gh_cli_setup() {
    local key_file=$1
    local project_id=$2
    
    echo ""
    echo "======================================"
    echo "GitHub CLI Secret Setup"
    echo "======================================"
    echo ""
    
    if ! command -v gh &> /dev/null; then
        echo -e "${YELLOW}GitHub CLI not installed. Manual setup required.${NC}"
        return 1
    fi
    
    # Check GitHub CLI authentication
    if ! gh auth status > /dev/null 2>&1; then
        echo "GitHub CLI not authenticated. Run: gh auth login"
        return 1
    fi
    
    echo "Setting secrets in your GitHub repository..."
    echo ""
    
    # Add secrets
    gh secret set GCP_SA_KEY < "$key_file" && \
        echo -e "${GREEN}✓ GCP_SA_KEY secret added${NC}" || \
        echo -e "${RED}❌ Failed to add GCP_SA_KEY${NC}"
    
    echo "$project_id" | gh secret set GCP_PROJECT_ID && \
        echo -e "${GREEN}✓ GCP_PROJECT_ID secret added${NC}" || \
        echo -e "${RED}❌ Failed to add GCP_PROJECT_ID${NC}"
    
    echo ""
    echo "Verifying secrets..."
    gh secret list | grep -E "GCP_SA_KEY|GCP_PROJECT_ID" || \
        echo -e "${YELLOW}Could not verify secrets${NC}"
    
    return 0
}

# Full setup
full_setup() {
    echo ""
    echo "======================================"
    echo "Full Automatic Setup for GCR"
    echo "======================================"
    echo ""
    
    read -p "Enter GCP Project ID: " project_id
    
    if [ -z "$project_id" ]; then
        echo -e "${RED}❌ Project ID is required${NC}"
        return
    fi
    
    read -p "Enter Service Account name (default: github-actions-gcr): " sa_name
    sa_name=${sa_name:-github-actions-gcr}
    
    echo ""
    
    # Enable API
    enable_cr_api "$project_id"
    echo ""
    
    # Create service account
    create_service_account "$project_id" "$sa_name"
    echo ""
    
    # Grant roles
    grant_sa_roles "$project_id" "$sa_name"
    echo ""
    
    # Create key
    read -p "Path to save key file (default: gcr-key.json): " key_file
    key_file=${key_file:-gcr-key.json}
    
    create_sa_key "$project_id" "$sa_name" "$key_file"
    echo ""
    
    # Try GitHub CLI first
    read -p "Use GitHub CLI to set secrets? (y/n): " use_gh
    if [ "$use_gh" = "y" ]; then
        if show_gh_cli_setup "$key_file" "$project_id"; then
            echo ""
            echo -e "${GREEN}✓ Setup complete!${NC}"
        else
            show_manual_setup "$key_file" "$project_id"
        fi
    else
        show_manual_setup "$key_file" "$project_id"
    fi
    
    echo ""
    echo -e "${GREEN}✓ Next steps:${NC}"
    echo "1. Verify secrets are in GitHub Settings"
    echo "2. Push changes to trigger workflow: git push"
    echo "3. Monitor in GitHub Actions tab"
    echo "4. View image with: gcloud container images list-tags gcr.io/$project_id/network-security-model"
}

# Main menu
show_menu() {
    echo "======================================"
    echo "Setup Options"
    echo "======================================"
    echo "1. Check prerequisites"
    echo "2. Enable Container Registry API"
    echo "3. Create service account"
    echo "4. Grant service account roles"
    echo "5. Create service account key"
    echo "6. Show manual setup instructions"
    echo "7. Full automatic setup"
    echo "0. Exit"
    echo ""
}

# Main loop
check_prerequisites

while true; do
    show_menu
    read -p "Select option (0-7): " option
    
    case $option in
        1)
            check_prerequisites
            ;;
        2)
            read -p "GCP Project ID: " project_id
            enable_cr_api "$project_id"
            ;;
        3)
            read -p "GCP Project ID: " project_id
            read -p "Service Account name: " sa_name
            create_service_account "$project_id" "$sa_name"
            ;;
        4)
            read -p "GCP Project ID: " project_id
            read -p "Service Account name: " sa_name
            grant_sa_roles "$project_id" "$sa_name"
            ;;
        5)
            read -p "GCP Project ID: " project_id
            read -p "Service Account name: " sa_name
            read -p "Output file path (default: gcr-key.json): " output_file
            output_file=${output_file:-gcr-key.json}
            create_sa_key "$project_id" "$sa_name" "$output_file"
            ;;
        6)
            read -p "Path to service account JSON key: " key_file
            read -p "GCP Project ID: " project_id
            show_manual_setup "$key_file" "$project_id"
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
