#!/bin/bash

# Define folders (without root directory)
FOLDERS=(
    "database"
    "modules"
    "web_ui/static"
    "web_ui/templates"
    "logs"
    "utils"
)

# Define files (without README & LICENSE since you already have them)
FILES=(
    "config.json"
    "server.py"
    "encryption.py"
    "authentication.py"
    "storage.py"
    "file_transfer.py"
    "modules/bot_integration.py"
    "modules/api_extension.py"
    "web_ui/app.py"
    "utils/generate_keys.py"
    "utils/backup_script.py"
    "requirements.txt"
)

# Create folders
for folder in "${FOLDERS[@]}"; do
    mkdir -p "$folder"
done

# Create empty files
for file in "${FILES[@]}"; do
    touch "$file"
done

# Default config.json content
echo '{
    "server_host": "0.0.0.0",
    "server_port": 5000,
    "encryption_enabled": true,
    "storage": {
        "local": true,
        "cloud_backup": false
    }
}' > "config.json"

echo "VoidLink-Server structure initialized successfully!"
