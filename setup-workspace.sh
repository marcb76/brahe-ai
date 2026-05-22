#!/bin/bash

# =============================================================
# brahe-ai: AI Agent based on Gemini: Information based on data
# Workspace initialization script (Python Version)
# 
# Marc Bonet
# Version 0.0.1
# May 2026
# =============================================================

clear
echo ""
echo ""
echo "==============================================================="
echo "# brahe-ai: AI Agent based on Gemini: Information based on data"
echo "# Tycho Brahe would be proud! 🪐"
echo "# https://en.wikipedia.org/wiki/Tycho_Brahe"
echo "#"
echo "# Workspace initialization script (Python Version)"
echo "# Designed for Windows environment with Python and Google APIs"
echo "#"
echo "#"
echo "# Marc Bonet"
echo "# Version 0.0.1"
echo "# May 2026"
echo "==============================================================="
echo ""
echo ""
echo ""
echo ""
echo "🚀 brahe-ai workspace setup (Python)..."

# Ensure required system tools are installed
echo "🔍 Checking required tools..."
for tool in git python; do
    if ! command -v $tool &> /dev/null; then
        echo "❌ $tool is not installed. Please install it first."
        exit 1
    fi
done
echo "✅ All required tools are installed."

# Initialize Git repository if it doesn't exist
if [ ! -d ".git" ]; then
    echo "🗃 Initializing git repository..."
    git init --initial-branch=main || { echo "Failed to initialize git repository"; exit 1; }
    echo "✅ Git repository initialized."

    echo "📝 Creating .gitignore..."
    cat << 'EOF' > .gitignore 
# Environment variables, secrets & Tokens
.env
credentials.json
token.json

# Runtime directories
log/
tmp/

# Python specific
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# OS / IDE files
.DS_Store
Thumbs.db
.vscode/
.history/
*.bak
*.tmp
*.log
EOF
    echo "✅ .gitignore created successfully."
else
    echo "ℹ️ Git repository already exists."
fi

# 3. Create Python virtual environment and install dependencies
echo ""
echo "🛠 Creating Python virtual environment (venv)..."
python -m venv venv || { echo "Failed to create virtual environment"; exit 1; }

# Activate venv temporarily to install dependencies within the script
# Detect if it's Windows or Unix for activation
if [ -d "venv/Scripts" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "📦 Installing Python dependencies (Gemini SDK, Google APIs, Excel tools)..."
pip install --upgrade pip
pip install google-auth-oauthlib google-api-python-client google-auth-httplib2 google-generativeai pandas openpyxl python-dotenv || { echo "Failed to install dependencies"; exit 1; }

# 4. Clean directory structure for the agent
echo ""
echo "🛠 Setting up directories..."
mkdir -p assets     # For static assets (e.g., license, documentation)
mkdir -p log        # For logging automated executions
mkdir -p tmp        # For temporary files (e.g., downloaded spreadsheets)
mkdir -p services    # For modular service scripts (e.g., google_drive.py, gmail.py, gemini_client.py)

# 5. Create the main agent script (brahe-ai.py)
echo "📝 Creating brahe-ai.py..."
cat << 'EOF' > brahe-ai.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
brahe-ai: AI Agent based on Gemini
Main Orchestrator
"""

import os
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

def main():
    print("===============================================================")
    print(" brahe-ai: AI Agent based on Gemini")
    print("           Information based on data")
    print("===============================================================")
    print("🤖 Agent initialized. Ready to process data on Windows...")
    
    # Next steps for the Lab:
    # 1. Authenticate with Google (Drive/Gmail)
    # 2. Search and download 'reporte.xlsx' and 'reglas.xlsx'
    # 3. Send data to Gemini
    # 4. Generate output and send via Gmail

if __name__ == "__main__":
    main()
EOF

# 6. Create license file (Preserving your terms of Puerto Rico)
echo "📄 Creating license file..."
cat > assets/license.txt << 'EOF'
Proprietary Software License Agreement

Copyright © 2026 Marc Bonet. All rights reserved.

This software and its associated documentation are proprietary products of Marc Bonet and are protected under applicable intellectual property laws of the United States and Puerto Rico. By installing, copying, or otherwise using this software, you agree to be bound by the terms of this license.
EOF

# 7. Create additional (empty) files for future development
touch credentials.json
touch token.json
touch services/__init__.py
touch services/google_service.py
touch services/gemini_service.py

# 8. Create .env file template
echo "🔐 Creating .env file template..."
cat << 'EOF' > .env
# Environment variables for brahe-ai
# Local Directories Configuration
DIR_TEMP_FOLDER="tmp"

# Google Drive Configuration (IDs de las carpetas en tu Drive)
DRIVE_INPUT_FOLDER_ID="your_input_folder_id_here"
DRIVE_OUTPUT_FOLDER_ID="your_output_folder_id_here"

# Gemini API Configuration
GEMINI_API_KEY="your_gemini_api_key_here"
EOF

echo "✅ All done!"
echo "✅ brahe-ai workspace setup complete!"
echo ""
echo "Next steps for your GitLab repository:"
echo "  1. git remote add origin https://gitlab.mbonet.xyz/username/brahe-ai.git"
echo "  2. git add ."
echo "  3. git commit -m 'Initial commit (Python Agent architecture)'"
echo "  4. git push --set-upstream origin main"
echo ""
echo ""
echo ""
