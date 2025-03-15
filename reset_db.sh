#!/bin/bash
# Script to reset the VoidLink database

echo "Resetting VoidLink database..."

# Remove database files
rm -rf database/users.json
rm -rf database/chat_log.json
rm -rf database/files/*
rm -rf database/chat_history/*
rm -rf database/encryption_key.json
rm -rf database/rooms.json
rm -rf database/file_metadata.json
rm -rf database/quarantine/*

# Recreate directories
mkdir -p database/files
mkdir -p database/chat_history
mkdir -p database/quarantine

# Create default users.json with admin account
echo '{
    "admin": {
        "password": "$2b$12$tOIreh07sMRCX9BT9pxDouVTJ8B5RNRpM0o5UlRmjSRm3C5dkiuEa",
        "role": "admin",
        "created_at": 1684156800,
        "device_ids": [],
        "failed_attempts": 0,
        "last_login": 1684156800
    }
}' > database/users.json

# Create empty chat_log.json
echo '[]' > database/chat_log.json

# Create empty rooms.json
echo '{
    "general": {
        "name": "General",
        "description": "General chat room",
        "created_by": "system",
        "created_at": 1684156800,
        "members": []
    }
}' > database/rooms.json

# Create empty file_metadata.json
echo '[]' > database/file_metadata.json

echo "Database reset complete!"