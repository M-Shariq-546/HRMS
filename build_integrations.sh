#!/bin/bash

# Horilla Integrations React App Build Script

echo "🚀 Building Horilla Integrations React App..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Built files are in: static/dist/js/"
    echo "🌐 Access the React version at: /integrations/integrations_react/"
    echo "📋 Access the Django template version at: /integrations/integrations_list/"
else
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo "1. Run your Django server"
echo "2. Navigate to /integrations/integrations_react/ for the React version"
echo "3. Navigate to /integrations/integrations_list/ for the Django template version"
echo ""
echo "For development, run: npm run dev" 