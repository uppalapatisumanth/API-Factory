@echo off
echo ========================================================
echo       Git FORCE Cleanup Helper 
echo ========================================================
echo.

echo [1/5] Removing frontend/node_modules from Git index...
git rm -r --cached frontend/node_modules
git rm -r --cached backend/venv

echo.
echo [2/5] Adding all other changes...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "FIX: Remove node_modules and venv"

echo.
echo [4/5] Pushing to GitHub (FORCE)...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo Standard push failed. Trying FORCE push...
    git push origin main --force
)

echo.
echo [5/5] Done.
echo NOW go to Vercel and click Redeploy.
