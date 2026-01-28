@echo off
setlocal
echo ========================================================
echo       GitHub Push Helper for API Factory
echo ========================================================
echo.

echo [0/5] Checking Git Identity...
for /f "tokens=*" %%i in ('git config user.name') do set CURRENT_NAME=%%i
for /f "tokens=*" %%i in ('git config user.email') do set CURRENT_EMAIL=%%i

if "%CURRENT_NAME%"=="" (
    echo Git User Name is NOT set.
    set /p GIT_NAME="Enter your Name (e.g. John Doe): "
    git config user.name "%GIT_NAME%"
) else (
    echo Found User Name: %CURRENT_NAME%
)

if "%CURRENT_EMAIL%"=="" (
    echo Git User Email is NOT set.
    set /p GIT_EMAIL="Enter your Email (e.g. john@example.com): "
    git config user.email "%GIT_EMAIL%"
) else (
    echo Found User Email: %CURRENT_EMAIL%
)

echo.
:ASK_URL
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/user/repo.git): "
if "%REPO_URL%"=="" goto ASK_URL

echo.
echo [1/5] Checking Git Status...
git status

echo.
echo [2/5] Adding Remote Origin...
git remote add origin %REPO_URL%
if %ERRORLEVEL% NEQ 0 (
    echo Remote 'origin' might already exist. Updating it...
    git remote set-url origin %REPO_URL%
)

echo.
echo [3/5] Renaming branch to main...
git branch -M main

echo.
echo [4/5] Adding files (ignoring excluded ones)...
git add .

echo.
echo [5/5] Committing and Pushing...
git commit -m "Initial push for distribution"

echo Attempting standard push...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo  CONFLICT DETECTED!
    echo ========================================================
    echo It looks like your GitHub repository already has some files
    echo (like a README or License) that you don't have locally.
    echo.
    echo Since this is an initial push, we can FORCE overwrite GitHub
    echo with your local files.
    echo.
    set /p FORCE_CHOICE="Do you want to FORCE PUSH (Overwrite GitHub)? (Y/N): "
    
    if /I "%FORCE_CHOICE%"=="Y" (
        echo.
        echo Overwriting GitHub with local files...
        git push -u origin main --force
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo SUCCESS! Forced push completed.
        ) else (
            echo.
            echo ERROR: Force push failed.
        )
    ) else (
        echo.
        echo You chose not to force push. You may need to run 'git pull' manually.
    )
) else (
    echo.
    echo ========================================================
    echo       SUCCESS! Project pushed to GitHub.
    echo ========================================================
)

pause
