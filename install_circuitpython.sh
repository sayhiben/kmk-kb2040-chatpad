#!/bin/bash
# Script to download and install CircuitPython on KB2040

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}CircuitPython KB2040 Installer${NC}"
echo "================================="

# CircuitPython version for KB2040
CP_VERSION="9.2.8"  # Latest stable as of now
DOWNLOAD_URL="https://downloads.circuitpython.org/bin/adafruit_kb2040/en_US/adafruit-circuitpython-adafruit_kb2040-en_US-${CP_VERSION}.uf2"

# Check for RPI-RP2 drive
if [ -d "/Volumes/RPI-RP2" ]; then
    MOUNT_POINT="/Volumes/RPI-RP2"
elif [ -d "/media/$USER/RPI-RP2" ]; then
    MOUNT_POINT="/media/$USER/RPI-RP2"
elif [ -d "/mnt/RPI-RP2" ]; then
    MOUNT_POINT="/mnt/RPI-RP2"
else
    echo -e "${RED}Error: RPI-RP2 drive not found${NC}"
    echo ""
    echo "To enter bootloader mode:"
    echo "1. Hold the BOOTSEL button on the KB2040"
    echo "2. Connect USB cable while holding the button"
    echo "3. Release the button"
    echo "4. RPI-RP2 drive should appear"
    echo ""
    echo "Alternative: Press RESET button twice quickly"
    exit 1
fi

echo -e "${YELLOW}Found RPI-RP2 at: $MOUNT_POINT${NC}"

# Download CircuitPython
echo "Downloading CircuitPython ${CP_VERSION}..."
curl -L -o circuitpython_kb2040.uf2 "$DOWNLOAD_URL"

if [ ! -f "circuitpython_kb2040.uf2" ]; then
    echo -e "${RED}Download failed!${NC}"
    echo "You can manually download from:"
    echo "$DOWNLOAD_URL"
    exit 1
fi

# Copy to device
echo "Installing CircuitPython..."
cp circuitpython_kb2040.uf2 "$MOUNT_POINT/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CircuitPython installed successfully!${NC}"
    echo ""
    echo "The KB2040 will reboot automatically."
    echo "Wait for CIRCUITPY drive to appear (5-10 seconds)."
    echo ""
    echo "Then run: ./deploy.sh"

    # Clean up
    rm circuitpython_kb2040.uf2
else
    echo -e "${RED}Failed to copy to device${NC}"
    exit 1
fi