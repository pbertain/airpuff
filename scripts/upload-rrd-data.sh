#!/bin/bash
# RRD Data Upload Script
# This script uploads RRD data to the server after successful deployment

set -e

# Configuration
RRD_DATA_PATH="/var/airpuff/rrd-data"
REMOTE_HOST="host74.nird.club"
REMOTE_USER="deploy"
REMOTE_PATH="/opt/airpuff/rrd-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 AirPuff RRD Data Upload Script${NC}"
echo "=================================="

# Check if RRD data directory exists
if [ ! -d "$RRD_DATA_PATH" ]; then
    echo -e "${RED}❌ Error: RRD data directory not found at $RRD_DATA_PATH${NC}"
    echo "Please ensure the RRD data directory exists and contains the RRD files."
    exit 1
fi

# Check if rsync is available
if ! command -v rsync &> /dev/null; then
    echo -e "${RED}❌ Error: rsync is not installed${NC}"
    echo "Please install rsync: sudo apt install rsync"
    exit 1
fi

# Check if SSH key is available
if [ ! -f "$HOME/.ssh/id_rsa" ] && [ ! -f "$HOME/.ssh/id_ed25519" ]; then
    echo -e "${RED}❌ Error: SSH key not found${NC}"
    echo "Please ensure you have an SSH key set up for $REMOTE_USER@$REMOTE_HOST"
    exit 1
fi

echo -e "${YELLOW}📊 RRD Data Information:${NC}"
echo "Source: $RRD_DATA_PATH"
echo "Destination: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo ""

# Show RRD data size
RRD_SIZE=$(du -sh "$RRD_DATA_PATH" | cut -f1)
echo -e "${YELLOW}📁 RRD Data Size: $RRD_SIZE${NC}"

# Count RRD files
RRD_COUNT=$(find "$RRD_DATA_PATH" -name "*.rrd" | wc -l)
echo -e "${YELLOW}📄 RRD Files: $RRD_COUNT${NC}"

# Confirm upload
echo ""
read -p "Do you want to proceed with the upload? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⏹️  Upload cancelled${NC}"
    exit 0
fi

echo -e "${GREEN}🔄 Starting RRD data upload...${NC}"

# Create remote directory if it doesn't exist
echo "Creating remote directory..."
ssh "$REMOTE_USER@$REMOTE_HOST" "sudo mkdir -p $REMOTE_PATH && sudo chown $REMOTE_USER:$REMOTE_USER $REMOTE_PATH"

# Upload RRD data using rsync
echo "Uploading RRD data..."
rsync -avz --progress --delete \
    --exclude="*.tmp" \
    --exclude="*.lock" \
    "$RRD_DATA_PATH/" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/"

# Set proper permissions
echo "Setting permissions..."
ssh "$REMOTE_USER@$REMOTE_HOST" "sudo chown -R $REMOTE_USER:$REMOTE_USER $REMOTE_PATH && sudo chmod -R 755 $REMOTE_PATH"

# Verify upload
echo "Verifying upload..."
REMOTE_COUNT=$(ssh "$REMOTE_USER@$REMOTE_HOST" "find $REMOTE_PATH -name '*.rrd' | wc -l")
echo -e "${GREEN}✅ Upload complete!${NC}"
echo "Local RRD files: $RRD_COUNT"
echo "Remote RRD files: $REMOTE_COUNT"

if [ "$RRD_COUNT" -eq "$REMOTE_COUNT" ]; then
    echo -e "${GREEN}✅ All RRD files uploaded successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: File count mismatch${NC}"
    echo "This might be normal if some files were excluded or if there are differences in the file structure."
fi

echo ""
echo -e "${GREEN}🎉 RRD data upload completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Run the migration: curl -X POST http://www.airpuff.info:25080/api/v1/migration/rrd/migrate"
echo "2. Check migration status: curl http://www.airpuff.info:25080/api/v1/migration/rrd/status"
echo "3. Validate migration: curl -X POST http://www.airpuff.info:25080/api/v1/migration/rrd/validate"
echo ""
echo "Or use the web interface:"
echo "http://www.airpuff.info:25080/migration"

