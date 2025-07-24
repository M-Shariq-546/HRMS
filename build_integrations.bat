@echo off
REM Horilla Integrations React App Build Script

echo 🚀 Building Horilla Integrations React App...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Build the React app
echo 🔨 Building React app...
npm run build

REM Check if build was successful
if %errorlevel% equ 0 (
    echo ✅ Build completed successfully!
    echo 📁 Built files are in: static/dist/js/
    echo 🌐 Access the React version at: /integrations/integrations_react/
    echo 📋 Access the Django template version at: /integrations/integrations_list/
) else (
    echo ❌ Build failed. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo 🎉 Setup complete! You can now:
echo 1. Run your Django server
echo 2. Navigate to /integrations/integrations_react/ for the React version
echo 3. Navigate to /integrations/integrations_list/ for the Django template version
echo.
echo For development, run: npm run dev
pause 