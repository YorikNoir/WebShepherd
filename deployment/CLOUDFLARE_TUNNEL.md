# Cloudflare Tunnel Configuration for WebShepherd

Add this ingress rule to your existing Cloudflare Tunnel configuration on Mac Mini.

## Configuration

Add to your `~/.cloudflared/config.yml` or wherever your tunnel config is located:

```yaml
tunnel: <your-tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  # WebShepherd - accessibility checker
  - hostname: yorik.space
    path: /webshepherd*
    service: http://localhost:8001

  # Existing rules for your website
  - hostname: yorik.space
    service: http://localhost:8080  # or your main site port

  # Catch-all rule (required)
  - service: http_status:404
```

## Alternative: Path-based routing only

If you want more specific routing:

```yaml
ingress:
  # WebShepherd API
  - hostname: yorik.space
    path: /webshepherd/api/*
    service: http://localhost:8001

  # WebShepherd Static Files
  - hostname: yorik.space
    path: /webshepherd/*
    service: http://localhost:8001

  # Main website
  - hostname: yorik.space
    service: http://localhost:8080

  - service: http_status:404
```

## After updating the configuration

```bash
# Restart cloudflared service
sudo systemctl restart cloudflared

# Or if running manually
sudo cloudflared tunnel run <tunnel-name>

# Check tunnel status
sudo cloudflared tunnel info <tunnel-name>
```

## Testing

Once deployed:
- Frontend: https://yorik.space/webshepherd/
- API Docs: https://yorik.space/api/docs
- Health Check: https://yorik.space/api/stats

## Notes

- WebShepherd runs on port 8001 (configured in deployment)
- Make sure the port doesn't conflict with other services
- The FastAPI app serves both static files (/webshepherd/) and API (/api/)
- API is accessible at both /api/* (direct) and /webshepherd/../api/* (through static mount)
