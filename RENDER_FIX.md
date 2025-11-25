# Fix: Dockerfile Not Found Error

## Problem
Render is looking for `Dockerfile` in the repo root, but it's in `mesh_cleanup_api/` directory.

## Solution: Update Render Settings

In your Render dashboard:

1. Go to your service settings
2. Find **"Root Directory"** or **"Dockerfile Path"** setting
3. Set it to one of these:

### Option 1: Set Root Directory (Recommended)
- **Root Directory:** `mesh_cleanup_api`
- **Dockerfile Path:** `./Dockerfile` (or leave blank)

### Option 2: Set Dockerfile Path
- **Root Directory:** `.` (root)
- **Dockerfile Path:** `mesh_cleanup_api/Dockerfile`

### Option 3: Use render.yaml (If using Blueprint)
The render.yaml should work, but make sure the root directory is set correctly.

## Quick Fix Steps:

1. In Render Dashboard → Your Service → Settings
2. Scroll to "Build & Deploy"
3. Set **Root Directory** to: `mesh_cleanup_api`
4. Save changes
5. Manual Deploy (or push a new commit to trigger auto-deploy)

The build should now find the Dockerfile!

