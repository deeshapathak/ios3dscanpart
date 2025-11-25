# Cloudflare Deployment Options

## Option 1: Cloudflare Workers (Python) - ⚠️ Limited

Cloudflare Workers now supports Python, but **Open3D will likely NOT work** because:
- Open3D has native C++ dependencies that may not be available in Workers
- CPU time limits (10ms-50s) may be too short for mesh processing
- Large file uploads may hit size limits
- Memory constraints

**However, you can try it:**
1. Use `pywrangler` CLI tool
2. Deploy FastAPI to Workers
3. Test if Open3D works (likely will fail, but worth trying)

**Setup:**
```bash
# Install pywrangler
pip install pywrangler

# Create wrangler.toml
# Deploy
pywrangler deploy
```

## Option 2: Cloudflare Tunnel (Recommended) ✅

Expose your self-hosted or cloud-hosted API through Cloudflare Tunnel. This gives you:
- Cloudflare's security (DDoS protection, WAF)
- Free SSL/TLS
- Global CDN (for static assets)
- Your Python API runs on a proper server

### Setup Steps:

1. **Host your API somewhere:**
   - Railway, Render, Fly.io, or your own server
   - Get the URL (e.g., `http://localhost:8000` or `https://your-api.railway.app`)

2. **Install Cloudflare Tunnel:**
   ```bash
   brew install cloudflared
   # Or download from: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

3. **Create Tunnel:**
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create mesh-api
   ```

4. **Configure Tunnel:**
   Create `config.yml`:
   ```yaml
   tunnel: <tunnel-id>
   credentials-file: /path/to/credentials.json
   
   ingress:
     - hostname: mesh-api.yourdomain.com
       service: http://localhost:8000
     - service: http_status:404
   ```

5. **Run Tunnel:**
   ```bash
   cloudflared tunnel run mesh-api
   ```

6. **Your API is now accessible at:** `https://mesh-api.yourdomain.com`

## Option 3: Cloudflare + Railway/Render (Best of Both Worlds) ⭐

1. **Deploy API to Railway/Render** (handles Python/Open3D)
2. **Use Cloudflare Tunnel** to expose it with:
   - Custom domain
   - DDoS protection
   - WAF rules
   - Analytics

**Example:**
- Railway URL: `https://mesh-api.railway.app`
- Cloudflare Tunnel exposes: `https://mesh-api.yourdomain.com`
- iOS app uses: `https://mesh-api.yourdomain.com`

## Recommendation

**For this use case (Open3D + large file processing):**

1. **Deploy to Railway/Render** (handles Python runtime properly)
2. **Use Cloudflare Tunnel** to add security and custom domain
3. **Or just use Railway/Render directly** (simpler, still secure)

Cloudflare Workers Python is too limited for Open3D. Use Cloudflare Tunnel instead to get Cloudflare's benefits while running the API on a proper server.

