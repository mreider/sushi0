#!/bin/bash

# Check if commit message and version are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Commit message or version not provided"
    exit 1
fi

# Define variables
commit_message=$1
version=$2

# Git operations
git add .
git commit -m "$commit_message"
git tag -a "$version" -m "$commit_message"
git push --follow-tags