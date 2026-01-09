@echo off
REM Deploy Unity Catalog Chatbot to Hugging Face Spaces (Windows)
REM This script automates the deployment process

echo ========================================================
echo  Unity Catalog Chatbot - Hugging Face Deployment
echo ========================================================
echo.

REM Configuration
set /p HF_USERNAME="Enter your Hugging Face username: "
set /p SPACE_NAME="Enter your Space name (e.g., unity-catalog-chatbot): "

set SPACE_URL=https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%

echo.
echo Deployment Configuration:
echo   Username: %HF_USERNAME%
echo   Space Name: %SPACE_NAME%
echo   Space URL: %SPACE_URL%
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo Error: git is not installed. Please install git first.
    exit /b 1
)

REM Create temporary directory for deployment
set DEPLOY_DIR=hf_deploy_temp
echo Creating deployment directory: %DEPLOY_DIR%
if exist %DEPLOY_DIR% rmdir /s /q %DEPLOY_DIR%
mkdir %DEPLOY_DIR%
cd %DEPLOY_DIR%

REM Initialize git repository
echo Initializing git repository...
git init
git lfs install

REM Add Hugging Face remote
echo Adding Hugging Face remote...
git remote add origin %SPACE_URL%

REM Copy necessary files
echo Copying application files...
copy ..\app.py .
copy ..\unity_catalog_service.py .
copy ..\unity-catalog-chatbot.jsx .
copy ..\index.html .
copy ..\requirements.txt .
copy ..\Dockerfile .
copy ..\config.py .
copy ..\conftest.py .
copy ..\.env.example .
copy ..\sample_queries.json .

REM Copy README with HF metadata
echo Preparing README...
copy ..\README_HF.md README.md

REM Create .gitignore
echo Creating .gitignore...
(
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo .Python
echo env/
echo venv/
echo .env
echo .venv
echo *.log
echo .pytest_cache/
echo .coverage
echo htmlcov/
echo dist/
echo build/
echo *.egg-info/
echo .DS_Store
) > .gitignore

REM Git add all files
echo Adding files to git...
git add .

REM Commit
echo Creating commit...
git commit -m "Initial deployment of Unity Catalog Chatbot"

REM Push to Hugging Face
echo.
echo Pushing to Hugging Face Spaces...
echo You may be prompted for your Hugging Face credentials
echo.
git push -u origin main --force

echo.
echo ========================================================
echo  Deployment Complete!
echo ========================================================
echo.
echo Next Steps:
echo   1. Visit your Space: %SPACE_URL%
echo   2. Go to Settings - Variables and secrets
echo   3. Add these secrets:
echo      - DATABRICKS_HOST: Your Databricks workspace URL
echo      - DATABRICKS_TOKEN: Your Databricks PAT
echo      - ANTHROPIC_API_KEY: Your Anthropic API key
echo   4. Wait for the Space to build (2-3 minutes^)
echo   5. Test your chatbot!
echo.
echo Space URL: %SPACE_URL%
echo.

REM Cleanup
cd ..
set /p CLEANUP="Remove deployment directory? (y/n): "
if /i "%CLEANUP%"=="y" (
    rmdir /s /q %DEPLOY_DIR%
    echo Cleanup complete
)

echo.
echo Deployment script finished!
pause
