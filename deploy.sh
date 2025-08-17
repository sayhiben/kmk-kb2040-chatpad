#!/bin/bash
# Deploy script for KMK KB2040 Chatpad driver

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}KMK KB2040 Chatpad Deployment Script${NC}"
echo "====================================="

# Check if CIRCUITPY mount point is provided or try to find it
if [ -z "$1" ]; then
    # Try to auto-detect CIRCUITPY mount point
    if [ -d "/Volumes/CIRCUITPY" ]; then
        MOUNT_POINT="/Volumes/CIRCUITPY"
    elif [ -d "/media/$USER/CIRCUITPY" ]; then
        MOUNT_POINT="/media/$USER/CIRCUITPY"
    elif [ -d "/mnt/CIRCUITPY" ]; then
        MOUNT_POINT="/mnt/CIRCUITPY"
    else
        echo -e "${RED}Error: CIRCUITPY mount point not found${NC}"
        echo "Usage: $0 [mount_point]"
        echo "Example: $0 /Volumes/CIRCUITPY"
        exit 1
    fi
else
    MOUNT_POINT="$1"
fi

# Verify mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo -e "${RED}Error: Mount point $MOUNT_POINT does not exist${NC}"
    exit 1
fi

echo -e "${YELLOW}Deploying to: $MOUNT_POINT${NC}"

# Deploy main files
echo "Copying main files..."
cp -v boot.py code.py config.py "$MOUNT_POINT/"

# Deploy lib directory structure
echo "Copying lib/chatpad..."
mkdir -p "$MOUNT_POINT/lib/chatpad"
cp -v lib/chatpad/*.py "$MOUNT_POINT/lib/chatpad/"

echo "Copying lib/macros..."
mkdir -p "$MOUNT_POINT/lib/macros"
cp -v lib/macros/*.py "$MOUNT_POINT/lib/macros/"

# Check if KMK is already installed
if [ ! -d "$MOUNT_POINT/lib/kmk" ]; then
    echo -e "${YELLOW}KMK not found on device. Installing...${NC}"
    
    # Check if submodule is initialized
    if [ ! -d "lib/kmk_firmware_repo/kmk" ]; then
        echo "Initializing git submodule..."
        git submodule init
        git submodule update
    fi
    
    # Copy KMK library
    echo "Copying KMK library (this may take a moment)..."
    cp -r lib/kmk_firmware_repo/kmk "$MOUNT_POINT/lib/"
    echo -e "${GREEN}KMK library installed${NC}"
else
    echo -e "${GREEN}KMK library already present${NC}"
fi

echo ""
echo -e "${GREEN}Deployment complete!${NC}"
echo "The device should automatically reload."
echo ""
echo "Hardware connections:"
echo "  - Chatpad TX → KB2040 RX"
echo "  - Chatpad RX → KB2040 TX"
echo "  - Power and ground"
echo ""
echo "To monitor serial output:"
echo "  screen /dev/tty.usbmodem* 115200"