#!/bin/bash

# Directory where all repos will be cloned
TARGET_DIR="data"

# List of GitHub repositories to clone
REPOS=(
    "https://github.com/digitalslidearchive/digital_slide_archive"
    "https://github.com/DigitalSlideArchive/HistomicsTK"
    "https://github.com/DigitalSlideArchive/ansible-role-vips"
    "https://github.com/DigitalSlideArchive/base_docker_image"
    "https://github.com/DigitalSlideArchive/dsa_girder_webix_base_viewer"
    "https://github.com/DigitalSlideArchive/DSA_Documentation"
    "https://github.com/DigitalSlideArchive/digitalslidearchive.info"
    "https://github.com/DigitalSlideArchive/pylibtiff"
    "https://github.com/DigitalSlideArchive/CNNCellDetection"
    "https://github.com/DigitalSlideArchive/ctk-cli"
    "https://github.com/DigitalSlideArchive/HistomicsUI"
    "https://github.com/DigitalSlideArchive/DSA-WSI-DeID"
    "https://github.com/DigitalSlideArchive/HistomicsStream"
    "https://github.com/DigitalSlideArchive/tifftools"
    "https://github.com/DigitalSlideArchive/annotation-tracker"
    "https://github.com/DigitalSlideArchive/ImageDePHI-Phase-I"
    "https://github.com/DigitalSlideArchive/HTAN"
    "https://github.com/DigitalSlideArchive/HistomicsDetect"
    "https://github.com/DigitalSlideArchive/girder-client-mount"
    "https://github.com/DigitalSlideArchive/ALBench"
    "https://github.com/DigitalSlideArchive/import-tracker"
    "https://github.com/DigitalSlideArchive/large-image-utilities"
    "https://github.com/DigitalSlideArchive/superpixel-classification"
    "https://github.com/DigitalSlideArchive/histoqc-dsa-plugin"
    "https://github.com/DigitalSlideArchive/wsi-superpixel-guided-labeling"
    "https://github.com/DigitalSlideArchive/ImageDePHI"
    "https://github.com/DigitalSlideArchive/large_image_source_isyntax"
    "https://github.com/DigitalSlideArchive/dive-dsa"
    "https://github.com/DigitalSlideArchive/girder_volview"
    "https://github.com/DigitalSlideArchive/histomics_load_testing"
    "https://github.com/DigitalSlideArchive/histomics-tour"
    "https://github.com/DigitalSlideArchive/dsa-run-custom-ai-models"
    "https://github.com/DigitalSlideArchive/girder-clamav"
    "https://github.com/DigitalSlideArchive/histomicstk-extras"
    "https://github.com/DigitalSlideArchive/girder_assetstore"
)

# Create the target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Loop through and clone each repo
for repo in "${REPOS[@]}"; do
    repo_name=$(basename "$repo" .git)
    target_path="${TARGET_DIR}/${repo_name}"

    if [ -d "$target_path/.git" ]; then
        echo "✅ Skipping existing repo: $repo_name"
    else:
        echo "📥 Cloning $repo into $target_path"
        git clone "$repo" "$target_path"
    fi
done

echo "✅ All repositories processed."
