#!/bin/bash
# Deploy script for KMK KB2040 Chatpad driver

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}KMK KB2040 Chatpad Deployment Script${NC}"
echo "====================================="

# Parse arguments
MOUNT_POINT=""
FORCE_KMK=false
DEBUG_MODE=false

# Show usage
show_usage() {
    echo "Usage: $0 [mount_point] [options]"
    echo "Options:"
    echo "  --force-kmk    Force reinstall KMK library even if present"
    echo "  --debug        Include debug and test files"
    echo ""
    echo "Examples:"
    echo "  $0                     # Auto-detect mount point"
    echo "  $0 /Volumes/CIRCUITPY  # Specify mount point"
    echo "  $0 --force-kmk         # Force reinstall KMK"
    echo "  $0 --debug --force-kmk # Debug mode with forced KMK"
}

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --force-kmk)
            FORCE_KMK=true
            ;;
        --debug)
            DEBUG_MODE=true
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            if [ -z "$MOUNT_POINT" ] && [ -d "$arg" ]; then
                MOUNT_POINT="$arg"
            elif [ -z "$MOUNT_POINT" ] && [[ ! "$arg" == --* ]]; then
                echo -e "${RED}Error: Invalid mount point: $arg${NC}"
                show_usage
                exit 1
            fi
            ;;
    esac
done

# Auto-detect mount point if not provided
if [ -z "$MOUNT_POINT" ]; then
    if [ -d "/Volumes/CIRCUITPY" ]; then
        MOUNT_POINT="/Volumes/CIRCUITPY"
    elif [ -d "/media/$USER/CIRCUITPY" ]; then
        MOUNT_POINT="/media/$USER/CIRCUITPY"
    elif [ -d "/mnt/CIRCUITPY" ]; then
        MOUNT_POINT="/mnt/CIRCUITPY"
    else
        echo -e "${RED}Error: CIRCUITPY mount point not found${NC}"
        show_usage
        exit 1
    fi
fi

# Verify mount point exists
if [ ! -d "$MOUNT_POINT" ]; then
    echo -e "${RED}Error: Mount point $MOUNT_POINT does not exist${NC}"
    exit 1
fi

echo -e "${YELLOW}Deploying to: $MOUNT_POINT${NC}"

# Show options
if [ "$FORCE_KMK" = true ]; then
    echo -e "${YELLOW}Options: Force KMK reinstall${NC}"
fi
if [ "$DEBUG_MODE" = true ]; then
    echo -e "${YELLOW}Options: Debug mode enabled${NC}"
fi

# Deploy main files
echo "Copying main files..."
cp -v boot.py code.py config.py "$MOUNT_POINT/"

# Copy test/debug files if requested
if [ "$DEBUG_MODE" = true ]; then
    echo -e "${YELLOW}Copying debug files...${NC}"
    cp -v code_debug.py test_*.py verify_kmk.py safe_mode.py "$MOUNT_POINT/" 2>/dev/null || true
fi

# Deploy lib directory structure
echo "Copying lib/chatpad..."
mkdir -p "$MOUNT_POINT/lib/chatpad"
cp -v lib/chatpad/*.py "$MOUNT_POINT/lib/chatpad/"

echo "Copying lib/macros..."
mkdir -p "$MOUNT_POINT/lib/macros"
cp -v lib/macros/*.py "$MOUNT_POINT/lib/macros/"

# Determine if KMK needs to be installed
INSTALL_KMK=false

if [ "$FORCE_KMK" = true ]; then
    echo -e "${YELLOW}Force reinstall of KMK requested${NC}"
    INSTALL_KMK=true
elif [ ! -d "$MOUNT_POINT/lib/kmk" ]; then
    echo -e "${YELLOW}KMK not found on device. Installing...${NC}"
    INSTALL_KMK=true
else
    # Check if critical subdirectories exist
    if [ ! -d "$MOUNT_POINT/lib/kmk/handlers" ] || [ ! -d "$MOUNT_POINT/lib/kmk/modules" ] || [ ! -f "$MOUNT_POINT/lib/kmk/scheduler.py" ]; then
        echo -e "${YELLOW}KMK installation incomplete. Reinstalling...${NC}"
        echo "  Missing components detected"
        INSTALL_KMK=true
    else
        echo -e "${GREEN}KMK library already present and complete${NC}"
        echo "  Use --force-kmk to reinstall anyway"
    fi
fi

if [ "$INSTALL_KMK" = true ]; then
    # Check if submodule is initialized
    if [ ! -d "lib/kmk_firmware_repo/kmk" ]; then
        echo "Initializing git submodule..."
        git submodule init
        git submodule update
    fi
    
    # Remove incomplete installation if exists
    if [ -d "$MOUNT_POINT/lib/kmk" ]; then
        echo "Removing incomplete KMK installation..."
        rm -rf "$MOUNT_POINT/lib/kmk"
    fi
    
    # Copy entire KMK library with all subdirectories
    echo "Copying complete KMK library (this may take a moment)..."
    cp -r lib/kmk_firmware_repo/kmk "$MOUNT_POINT/lib/"
    
    # Verify critical directories
    if [ -d "$MOUNT_POINT/lib/kmk/handlers" ] && [ -d "$MOUNT_POINT/lib/kmk/modules" ]; then
        echo -e "${GREEN}✓ KMK library installed successfully${NC}"
    else
        echo -e "${RED}⚠ KMK installation may be incomplete${NC}"
    fi
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