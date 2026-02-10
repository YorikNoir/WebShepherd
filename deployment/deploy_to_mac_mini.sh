#!/bin/bash
#
# deploy_to_mac_mini.sh
# Automated deployment script for WebShepherd to Mac Mini
#
# Usage: ./deploy_to_mac_mini.sh

set -e  # Exit on error

# Configuration
MAC_MINI_USER="throwaway"
MAC_MINI_HOST="192.168.2.201"
MAC_MINI_PATH="/home/throwaway/webshepherd"
SERVICE_NAME="webshepherd.service"

echo "🐑 WebShepherd Deployment to Mac Mini"
echo "======================================"
echo ""

# Check if SSH key is set up
echo "Testing SSH connection..."
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 ${MAC_MINI_USER}@${MAC_MINI_HOST} exit 2>/dev/null; then
    echo "❌ Cannot connect to Mac Mini. Please set up SSH keys first:"
    echo "   ssh-copy-id ${MAC_MINI_USER}@${MAC_MINI_HOST}"
    exit 1
fi
echo "✅ SSH connection successful"
echo ""

# Sync files (excluding venv, __pycache__, etc.)
echo "📦 Syncing files to Mac Mini..."
rsync -avz --delete \
    --exclude='venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='webshepherd.db' \
    --exclude='.git/' \
    --exclude='node_modules/' \
    ../backend/ ${MAC_MINI_USER}@${MAC_MINI_HOST}:${MAC_MINI_PATH}/backend/

echo "✅ Files synced"
echo ""

# Remote deployment commands
echo "🚀 Running deployment commands on Mac Mini..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} << 'ENDSSH'
    set -e
    cd /home/throwaway/webshepherd/backend

    echo "Setting up Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    echo "Activating virtual environment..."
    source venv/bin/activate

    echo "Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt

    echo "Checking .env file..."
    if [ ! -f ".env" ]; then
        echo "⚠️  .env file not found. Creating from example..."
        cp .env.example .env
        echo "⚠️  IMPORTANT: Edit /home/throwaway/webshepherd/backend/.env with production settings!"
    fi

    echo "✅ Backend setup complete"
ENDSSH

echo ""
echo "🔄 Restarting WebShepherd service..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} << 'ENDSSH'
    # Restart service if it exists
    if sudo systemctl is-active --quiet webshepherd.service; then
        echo "Restarting service..."
        sudo systemctl restart webshepherd.service
        sleep 2
        if sudo systemctl is-active --quiet webshepherd.service; then
            echo "✅ Service restarted successfully"
        else
            echo "❌ Service failed to restart. Check logs:"
            echo "   sudo journalctl -u webshepherd.service -n 50"
            exit 1
        fi
    else
        echo "⚠️  Service not found. You need to set it up first."
        echo "See deployment/MAC_MINI_DEPLOYMENT.md for instructions"
    fi
ENDSSH

echo ""
echo "🧪 Testing API..."
sleep 1
API_RESPONSE=$(ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "curl -s http://127.0.0.1:8001/" || echo "")

if echo "$API_RESPONSE" | grep -q "WebShepherd"; then
    echo "✅ API is responding correctly"
else
    echo "❌ API is not responding. Check logs:"
    echo "   ssh ${MAC_MINI_USER}@${MAC_MINI_HOST}"
    echo "   sudo journalctl -u webshepherd.service -f"
    exit 1
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "sudo systemctl status webshepherd.service --no-pager | head -20"
echo ""
echo "🌐 WebShepherd should be available at:"
echo "   https://yorik.space/webshepherd/docs"
echo ""
echo "📝 View logs:"
echo "   ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} 'sudo journalctl -u webshepherd.service -f'"
echo ""
