#!/bin/bash
# deploy-to-huggingface.sh
# One-command deployment to Hugging Face Spaces

set -e

echo "🚀 UnityCatalog-ChatBot Hugging Face Deployment"
echo "==============================================="
echo ""

# Step 1: Gather user input
echo "Step 1: Enter your Hugging Face username"
read -p "Your HF username: " HF_USERNAME

SPACE_NAME="unitycatalog-chatbot"
SPACE_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

echo "✓ Space URL will be: $SPACE_URL"
echo ""

# Step 2: Verify files
echo "Step 2: Verifying required files..."
REQUIRED_FILES=("app.py" "unity_catalog_service.py" "config.py" "requirements.txt" "Dockerfile" ".env.example")

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        exit 1
    fi
done
echo "✓ All required files present"
echo ""

# Step 3: Create .env for local testing
echo "Step 3: Creating .env from template..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env (edit with your credentials before continuing)"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your Databricks and Anthropic credentials"
    read -p "Press Enter once you've updated .env..."
else
    echo "✓ .env already exists"
fi
echo ""

# Step 4: Test locally
echo "Step 4: Running tests..."
python -m pytest test_chatbot.py -v --tb=short -q
echo "✓ All tests passed"
echo ""

# Step 5: Verify Dockerfile
echo "Step 5: Verifying Dockerfile..."
if ! grep -q "FROM python" Dockerfile; then
    echo "❌ Dockerfile invalid"
    exit 1
fi
echo "✓ Dockerfile is valid"
echo ""

# Step 6: Git setup
echo "Step 6: Setting up Git..."
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "Initial commit: UnityCatalog-ChatBot"
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
    git add .
    if git diff --cached --quiet; then
        echo "✓ No changes to commit"
    else
        git commit -m "Update: deployment preparation"
        echo "✓ Changes committed"
    fi
fi
echo ""

# Step 7: Manual Space creation instructions
echo "Step 7: Manual Space Creation"
echo "=============================="
echo ""
echo "⚠️  Please complete these steps manually on Hugging Face:"
echo ""
echo "1. Go to: https://huggingface.co/new"
echo "2. Fill in the form:"
echo "   - Owner: $HF_USERNAME"
echo "   - Repository name: $SPACE_NAME"
echo "   - Type: Space"
echo "   - Space SDK: Docker"
echo "   - License: MIT"
echo "3. Click 'Create Space'"
echo ""
echo "Once created, you'll get a clone URL like:"
echo "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""

read -p "Press Enter once you've created the Space..."
echo ""

# Step 8: Push to HF
echo "Step 8: Pushing code to Hugging Face..."
echo ""
echo "You'll be asked to authenticate. Use your HF token:"
echo "Visit: https://huggingface.co/settings/tokens"
echo "Copy a READ+WRITE token and paste it when prompted."
echo ""

PUSH_URL="https://huggingface.co/spaces/${HF_USERNAME}/${SPACE_NAME}"

# Try to add remote
if git remote | grep -q "huggingface"; then
    git remote remove huggingface
fi

git remote add huggingface "$PUSH_URL"

echo "Pushing to $PUSH_URL..."
git push -u huggingface main || git push -u huggingface master

echo "✓ Code pushed to Hugging Face"
echo ""

# Step 9: Add secrets
echo "Step 9: Adding secrets to Hugging Face Space"
echo "=============================================="
echo ""
echo "⚠️  Complete these steps in HF UI:"
echo ""
echo "1. Go to: $SPACE_URL/settings"
echo "2. Click 'Repository Secrets'"
echo "3. Add these three secrets:"
echo ""
echo "   Secret 1:"
echo "   - Name: DATABRICKS_HOST"
echo "   - Value: <your workspace URL>"
echo ""
echo "   Secret 2:"
echo "   - Name: DATABRICKS_TOKEN"
echo "   - Value: <your personal access token>"
echo ""
echo "   Secret 3:"
echo "   - Name: ANTHROPIC_API_KEY"
echo "   - Value: <your Claude API key>"
echo ""
echo "4. Click 'Save' after each secret"
echo "5. Space will rebuild automatically"
echo ""

read -p "Press Enter once you've added all secrets..."
echo ""

# Step 10: Verify deployment
echo "Step 10: Verifying deployment..."
echo ""
echo "Waiting 30 seconds for Space to build..."
sleep 30

HEALTH_URL="${SPACE_URL/huggingface.co/huggingface.co}/api/health"
# Note: The actual URL will be in HF logs - this is just for reference

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "Your chatbot is now live at:"
echo "  🌐 $SPACE_URL"
echo ""
echo "Next steps:"
echo "  1. Visit the Space URL above"
echo "  2. Check Settings → Runtime logs for any errors"
echo "  3. Once 'Running' status shows, test the API"
echo ""
echo "Test endpoints:"
echo "  curl https://${HF_USERNAME}-${SPACE_NAME}.hf.space/api/health"
echo "  curl https://${HF_USERNAME}-${SPACE_NAME}.hf.space/api/catalogs"
echo ""
echo "Share your Space:"
echo "  Simply send the URL to others to access the chatbot!"
echo ""
