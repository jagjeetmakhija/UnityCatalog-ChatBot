#!/bin/bash
# Deploy Unity Catalog Chatbot to Hugging Face Spaces
# This script automates the deployment process

set -e

echo "🚀 Unity Catalog Chatbot - Hugging Face Deployment Script"
echo "=========================================================="

# Configuration
read -p "Enter your Hugging Face username: " HF_USERNAME
read -p "Enter your Space name (e.g., unity-catalog-chatbot): " SPACE_NAME

SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"

echo ""
echo "📋 Deployment Configuration:"
echo "  Username: $HF_USERNAME"
echo "  Space Name: $SPACE_NAME"
echo "  Space URL: $SPACE_URL"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed. Please install git first."
    exit 1
fi

# Check if user is logged into Hugging Face
if ! git config --get credential.helper | grep -q "huggingface"; then
    echo "⚠️  Warning: You may need to configure Hugging Face git credentials"
    echo "   Run: git config --global credential.helper store"
    echo ""
fi

# Create temporary directory for deployment
DEPLOY_DIR="hf_deploy_temp"
echo "📁 Creating deployment directory: $DEPLOY_DIR"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

# Initialize git repository
echo "🔧 Initializing git repository..."
git init
git lfs install

# Add Hugging Face remote
echo "🔗 Adding Hugging Face remote..."
git remote add origin $SPACE_URL

# Copy necessary files
echo "📦 Copying application files..."
cp ../app.py .
cp ../unity_catalog_service.py .
cp ../unity-catalog-chatbot.jsx .
cp ../index.html .
cp ../requirements.txt .
cp ../Dockerfile .
cp ../config.py .
cp ../conftest.py .
cp ../.env.example .
cp ../sample_queries.json .

# Copy README with HF metadata
echo "📄 Preparing README..."
cp ../README_HF.md README.md

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv
*.log
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.DS_Store
EOF

# Git add all files
echo "➕ Adding files to git..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "Initial deployment of Unity Catalog Chatbot"

# Push to Hugging Face
echo ""
echo "🚀 Pushing to Hugging Face Spaces..."
echo "   You may be prompted for your Hugging Face credentials"
echo ""
git push -u origin main --force

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📍 Next Steps:"
echo "   1. Visit your Space: $SPACE_URL"
echo "   2. Go to Settings → Variables and secrets"
echo "   3. Add these secrets:"
echo "      - DATABRICKS_HOST: Your Databricks workspace URL"
echo "      - DATABRICKS_TOKEN: Your Databricks personal access token"
echo "      - ANTHROPIC_API_KEY: Your Anthropic API key"
echo "   4. Wait for the Space to build (2-3 minutes)"
echo "   5. Test your chatbot!"
echo ""
echo "🔗 Space URL: $SPACE_URL"
echo ""

# Cleanup
cd ..
read -p "Remove deployment directory? (y/n): " CLEANUP
if [ "$CLEANUP" == "y" ]; then
    rm -rf $DEPLOY_DIR
    echo "✨ Cleanup complete"
fi

echo ""
echo "🎉 Deployment script finished!"
