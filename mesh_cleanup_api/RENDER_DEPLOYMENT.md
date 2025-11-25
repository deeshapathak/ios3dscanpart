# Deploying to Render

## Quick Deploy Steps

### Option 1: Deploy from GitHub (Recommended)

1. **Push your code to GitHub:**
   ```bash
   cd mesh_cleanup_api
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Go to Render Dashboard:**
   - Visit https://dashboard.render.com
   - Sign in with GitHub

3. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `mesh_cleanup_api` directory

4. **Configure:**
   - **Name:** `mesh-cleanup-api` (or your choice)
   - **Environment:** `Docker`
   - **Dockerfile Path:** `./Dockerfile` (or leave default)
   - **Docker Context:** `.` (or leave default)
   - **Plan:** 
     - **Free** - Good for testing (spins down after inactivity)
     - **Starter ($7/month)** - Better for production (always on)

5. **Environment Variables (Optional):**
   - Add any custom config if needed

6. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Wait 5-10 minutes for first deployment

7. **Get Your URL:**
   - Once deployed, you'll get a URL like: `https://mesh-cleanup-api.onrender.com`
   - This is your API endpoint!

### Option 2: Deploy with render.yaml (Blueprints)

1. **Push code with render.yaml** (already created in repo)

2. **Go to Render Dashboard:**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render will detect `render.yaml` automatically

3. **Review and Deploy:**
   - Review the service configuration
   - Click "Apply"
   - Render deploys automatically

## Update Your iOS App

Once deployed, update your iOS app:

```swift
let cleanupService = MeshCleanupService(
    baseURL: "https://mesh-cleanup-api.onrender.com"  // Your Render URL
)
```

## Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30-50 seconds (cold start)
- 750 hours/month free
- Good for testing/development

### Starter Plan ($7/month):
- **Always on** (no cold starts)
- Better for production
- Faster response times
- More reliable

### File Size Limits:
- Render has request size limits
- For very large PLY files (>10MB), consider:
  - Using Starter plan (higher limits)
  - Implementing chunked uploads
  - Or using Render's file storage

## Testing Your Deployment

Once deployed, test with:

```bash
# Health check
curl https://your-app.onrender.com/

# Test mesh cleaning (replace with your PLY file)
curl -X POST "https://your-app.onrender.com/clean-mesh?return_format=ply" \
  -F "file=@scan.ply" \
  -o cleaned_mesh.ply
```

## Monitoring

- View logs in Render dashboard
- Check service health
- Monitor response times
- View error logs if issues occur

## Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed
5. Your API will be available at your custom domain

## Troubleshooting

### Build Fails:
- Check Dockerfile is correct
- Verify Python 3.10 in Dockerfile
- Check build logs in Render dashboard

### Service Crashes:
- Check logs in Render dashboard
- Verify Open3D is installing correctly
- Check memory limits (free tier has limits)

### Slow Response:
- Free tier has cold starts (30-50s first request)
- Upgrade to Starter plan for always-on
- Check if PLY file is too large

## Next Steps

1. Deploy to Render
2. Test the API endpoint
3. Update iOS app with Render URL
4. Test end-to-end from iOS app
5. Consider upgrading to Starter plan for production

