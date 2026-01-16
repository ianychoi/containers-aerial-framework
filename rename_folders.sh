#!/bin/bash

# Remove 90-credits folder
rm -rf content/90-credits

# Rename folders to remove number prefixes
mv content/20-introduction content/introduction
mv content/30-docker-basics content/docker-basics
mv content/40-container-environment content/container-environment
mv content/50-git-management content/git-management
mv content/60-integrated-workflow content/integrated-workflow
mv content/70-eks content/eks
mv content/80-summary content/summary

echo "Folders renamed successfully!"
