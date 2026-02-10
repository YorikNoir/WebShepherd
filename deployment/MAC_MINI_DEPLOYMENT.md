# WebShepherd Deployment - Mac Mini Configuration

## Server Details
- **Host:** throwaway@192.168.2.201
- **Deployment Path:** `/home/throwaway/webshepherd`
- **Service Port:** 8001 (to avoid conflict with other services)
- **Public URL:** https://yorik.space/webshepherd (via Cloudflare Tunnel)

## Prerequisites on Mac Mini

```bash
# Python 3.9+
python3 --version

# pip
pip3 --version

# virtualenv
pip3 install virtualenv

# Cloudflare Tunnel (cloudflared) should already be configured
cloudflared --version
```

## Deployment Steps

### 1. Copy files to Mac Mini

```bash
# From Windows development machine
scp -r d:/Projects/WebShepherd throwaway@192.168.2.201:~/
```

### 2. SSH into Mac Mini

```bash
ssh throwaway@192.168.2.201
```

### 3. Set up Python environment

```bash
cd ~/webshepherd/backend

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure environment

```bash
# Create .env file
cp .env.example .env

# Edit settings for Mac Mini
nano .env
```

Update `.env`:
```bash
DEBUG=False
DATABASE_URL=sqlite+aiosqlite:////home/throwaway/webshepherd/backend/webshepherd.db
ALLOWED_ORIGINS=https://yorik.space,https://www.yorik.space
RATE_LIMIT_PER_HOUR=10
```

### 5. Initialize database

```bash
# Test run
python main.py

# Stop with Ctrl+C after seeing "Database initialized"
```

### 6. Create systemd service

```bash
sudo nano /etc/systemd/system/webshepherd.service
```

Paste:
```ini
[Unit]
Description=WebShepherd WCAG Accessibility Checker
After=network.target

[Service]
Type=simple
User=throwaway
WorkingDirectory=/home/throwaway/webshepherd/backend
Environment="PATH=/home/throwaway/webshepherd/backend/venv/bin"
ExecStart=/home/throwaway/webshepherd/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7. Start service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start
sudo systemctl enable webshepherd.service

# Start service
sudo systemctl start webshepherd.service

# Check status
sudo systemctl status webshepherd.service

# View logs
sudo journalctl -u webshepherd.service -f
```

### 8. Configure Cloudflare Tunnel

Update your existing Cloudflare Tunnel configuration to route `/webshepherd/*` to the WebShepherd service.

See **[CLOUDFLARE_TUNNEL.md](CLOUDFLARE_TUNNEL.md)** for detailed configuration.

**Quick setup:**
```bash
# Edit your tunnel config (location may vary)
nano ~/.cloudflared/config.yml

# Add this ingress rule BEFORE your catch-all rule:
#   - hostname: yorik.space
#     path: /webshepherd*
#     service: http://localhost:8001

# Restart cloudflared
sudo systemctl restart cloudflared

# Check status
sudo systemctl status cloudflared
```

### 9. Verify deployment

```bash
# Test API locally
curl http://127.0.0.1:8001/
curl http://127.0.0.1:8001/api/stats

# Test via Cloudflare Tunnel
curl https://yorik.space/webshepherd/
curl https://yorik.space/api/stats
```

**Note:** The frontend is served by FastAPI at `/webshepherd/`, and the API is accessible at `/api/*`

## Maintenance

### View logs
```bash
sudo journalctl -u webshepherd.service -f
```

### Restart service
```bash
sudo systemctl restart webshepherd.service
```

### Update code
```bash
cd ~/webshepherd
git pull  # if using git
sudo systemctl restart webshepherd.service
```

### Database backup
```bash
cp ~/webshepherd/backend/webshepherd.db ~/webshepherd/backend/webshepherd.db.backup
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u webshepherd.service -n 100

# Test manually
cd ~/webshepherd/backend
source venv/bin/activate
python main.py
```

### Port already in use
```bash
# Check what's using port 8001
sudo lsof -i :8001

# Kill process if needed
sudo kill -9 <PID>
```

### Database locked
```bash
# Stop service
sudo systemctl stop webshepherd.service

# Remove lock
rm ~/webshepherd/backend/webshepherd.db-shm
rm ~/webshepherd/backend/webshepherd.db-wal

# Restart
sudo systemctl start webshepherd.service
```

## Security Notes

- API runs on 127.0.0.1 only (not exposed directly)
- Rate limiting enabled (10 scans/hour per IP)
- Max file size: 5MB
- Request timeout: 10 seconds
- No JavaScript execution (safe)
- No access to private IPs

## Resource Usage

**Expected:**
- Memory: ~100-200 MB
- CPU: Low (spikes during scans)
- Disk: Minimal (database grows slowly)

Perfect for Mac Mini 2018!
