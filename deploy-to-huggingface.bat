@echo off
REM deploy-to-huggingface.bat
REM Windows deployment to Hugging Face Spaces

setlocal enabledelayedexpansion

echo.
echo ========================================
echo ^(^) UnityCatalog-ChatBot HF Deployment
echo ========================================
echo.

REM Step 1: Get HF username
set /p HF_USERNAME="Enter your Hugging Face username: "
set SPACE_NAME=unitycatalog-chatbot
set SPACE_URL=https://huggingface.co/spaces/%HF_USERNAME%/%SPACE_NAME%

echo.
echo Space URL: %SPACE_URL%
echo.

REM Step 2: Verify files
echo Verifying required files...
for %%F in (app.py unity_catalog_service.py config.py requirements.txt Dockerfile .env.example) do (
    if not exist "%%F" (
        echo Error: Missing %%F
        exit /b 1
    )
)
echo OK - All files present
echo.

REM Step 3: Test locally
echo Running tests...
python -m pytest test_chatbot.py -v --tb=short -q
if errorlevel 1 (
    echo Tests failed!
    exit /b 1
)
echo OK - Tests passed
echo.

REM Step 4: .env setup
if not exist ".env" (
    copy .env.example .env
    echo Created .env - please edit with your credentials
    pause
)
echo.

REM Step 5: Git setup
if not exist ".git" (
    echo Initializing git...
    git init
    git add .
    git commit -m "Initial commit: UnityCatalog-ChatBot"
) else (
    echo Git already initialized
    git add .
    git diff --cached --quiet
    if errorlevel 0 (
        git commit -m "Update: deployment preparation"
    )
)
echo.

REM Step 6: Instructions
echo.
echo ========================================
echo Manual Steps Required:
echo ========================================
echo.
echo 1. Create Space on Hugging Face:
echo    https://huggingface.co/new
echo    - Repository name: %SPACE_NAME%
echo    - Type: Space
echo    - SDK: Docker
echo.
echo 2. Once created, run this command:
echo    git remote add huggingface %SPACE_URL%
echo    git push -u huggingface main
echo.
echo 3. Add Secrets in Space Settings:
echo    - DATABRICKS_HOST
echo    - DATABRICKS_TOKEN
echo    - ANTHROPIC_API_KEY
echo.
echo 4. Space rebuilds automatically (2-5 min)
echo.
echo 5. Test at: https://%HF_USERNAME%-%SPACE_NAME%.hf.space/api/health
echo.
pause

echo ========================================
echo Deployment Complete!
echo ========================================
echo Your chatbot: %SPACE_URL%
