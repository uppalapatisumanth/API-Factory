@echo off
echo ========================================================
echo       Git Cleanup Helper 
echo ========================================================
echo.
echo This script will remove 'node_modules' and 'venv' from GitHub
echo if they were accidentally uploaded. This fixes Vercel errors.
echo.

echo [1/4] Removing frontend/node_modules from Git index...
git rm -r --cached frontend/node_modules
if %ERRORLEVEL% NEQ 0 (
    echo (It was not tracked, skipping...)
)

echo.
echo [2/4] Removing backend/venv from Git index...
git rm -r --cached backend/venv
if %ERRORLEVEL% NEQ 0 (
    echo (It was not tracked, skipping...)
)

echo.
echo [3/4] Committing changes...
git commit -m "Fix: Remove ignored node_modules/venv from git"
if %ERRORLEVEL% NEQ 0 (
    echo No changes to commit.
)

echo.
echo [4/4] Pushing to GitHub...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Push failed. Please run 'push_to_github.bat' manually if needed.
) else (
    echo.
    echo SUCCESS! Cleaned up repository.
    echo Now Redploy on Vercel.
)


