# Cloudflare Tunnel Setup for WebShepherd

## ✅ Deployment Status

WebShepherd is now running on your Mac Mini at `localhost:8001` with auto-start enabled via launchd.

- **Backend**: Running on port 8001
- **Frontend**: Accessible at http://localhost:8001/webshepherd/
- **API**: Available at http://localhost:8001/api/*
- **Service**: Configured to start automatically on boot
- **Logs**:
  - Output: `/Users/throwaway/webshepherd/webshepherd.log`
  - Errors: `/Users/throwaway/webshepherd/webshepherd.error.log`

## 🌐 Cloudflare Tunnel Configuration

Your Mac Mini is using a token-based Cloudflare Tunnel (managed via dashboard).

### Add WebShepherd to Your Tunnel

1. **Log in to Cloudflare Dashboard**
   - Go to https://dash.cloudflare.com/
   - Select your account
   - Navigate to **Zero Trust** > **Access** > **Tunnels**

2. **Edit Your Existing Tunnel**
   - Find your active tunnel (connected to yorik.space)
   - Click **Configure**
   - Go to the **Public Hostname** tab

3. **Add WebShepherd Route**
   - Click **Add a public hostname**
   - Configure as follows:
     ```
     Subdomain: (leave empty or use your current subdomain)
     Domain: yorik.space
     Path: /webshepherd*
     Type: HTTP
     URL: localhost:8001
     ```

4. **Save Configuration**
   - Click **Save hostname**
   - The tunnel will automatically reload with the new configuration

### Alternative: Add as Catch-All

If you want WebShepherd at a subdomain (e.g., `webshepherd.yorik.space`):

```
Subdomain: webshepherd
Domain: yorik.space
Path: (leave empty)
Type: HTTP
URL: localhost:8001
```

## 🧪 Testing

After configuring the tunnel:

1. **Test Frontend**:
   ```bash
   curl https://yorik.space/webshepherd/
   ```

2. **Test API**:
   ```bash
   curl https://yorik.space/api/stats
   ```

3. **Browser Test**:
   - Navigate to: https://yorik.space/webshepherd
   - Enter a test URL (e.g., https://example.com)
   - Click **Scan Website**
   - Verify results appear

## 🔄 Service Management

### Check Service Status
```bash
launchctl list | grep webshepherd
```

### View Logs
```bash
tail -f ~/webshepherd/webshepherd.log
tail -f ~/webshepherd/webshepherd.error.log
```

### Restart Service
```bash
launchctl unload ~/Library/LaunchAgents/com.webshepherd.plist
launchctl load ~/Library/LaunchAgents/com.webshepherd.plist
```

### Stop Service
```bash
launchctl unload ~/Library/LaunchAgents/com.webshepherd.plist
```

### Start Service
```bash
launchctl load ~/Library/LaunchAgents/com.webshepherd.plist
```

## 🐛 Troubleshooting

### Service Not Starting
1. Check logs: `cat ~/webshepherd/webshepherd.error.log`
2. Verify venv exists: `ls ~/webshepherd/backend/venv/bin/python`
3. Test manually: `cd ~/webshepherd/backend && ~/webshepherd/backend/venv/bin/python -m uvicorn main:app --port 8001`

### Cloudflare Tunnel Not Routing
1. Verify tunnel is running: `ps aux | grep cloudflared`
2. Check Cloudflare dashboard for tunnel status
3. Ensure path is `/webshepherd*` (with wildcard)
4. Clear browser cache and retry

### API Returns 404
1. Test local API: `curl http://localhost:8001/api/stats`
2. Check if service is running: `launchctl list | grep webshepherd`
3. Verify Cloudflare route includes `/api/*` path

## 📊 Monitoring

Check WebShepherd statistics:
```bash
curl http://localhost:8001/api/stats | python3 -m json.tool
```

Expected response:
```json
{
    "total_scans": 0,
    "scans_today": 0,
    "average_score": 0.0,
    "common_issues": []
}
```

## 🚀 Next Steps

1. ✅ Update Cloudflare Tunnel configuration (add /webshepherd route)
2. ✅ Test public access at https://yorik.space/webshepherd
3. ✅ Verify the CV link works: Check your CV project list
4. ✅ Run a test scan to ensure end-to-end functionality

---

**Note**: Your Cloudflare Tunnel is token-based, meaning all configuration is managed through the Cloudflare Dashboard, not via local config files. This makes it easier to manage but requires dashboard access for route updates.
