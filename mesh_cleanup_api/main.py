"""
FastAPI backend for cleaning PLY point cloud files from TrueDepth camera scans.
Optimized for face/rhinoplasty scans.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import open3d as o3d
import numpy as np
import tempfile
import os
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Mesh Cleanup API", version="1.0.0")

# Enable CORS for iOS app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your iOS app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def clean_point_cloud(pcd: o3d.geometry.PointCloud) -> o3d.geometry.PointCloud:
    """
    Clean point cloud by removing outliers and noise.
    Optimized for face scans from TrueDepth camera.
    """
    logger.info(f"Original point count: {len(pcd.points)}")
    
    # Statistical outlier removal - removes points that are far from their neighbors
    pcd, statistical_ind = pcd.remove_statistical_outlier(
        nb_neighbors=20,  # Number of neighbors to consider
        std_ratio=2.0      # Standard deviation ratio threshold
    )
    logger.info(f"After statistical outlier removal: {len(pcd.points)}")
    
    # Radius outlier removal - removes isolated points
    pcd, radius_ind = pcd.remove_radius_outlier(
        nb_points=16,      # Minimum number of points within radius
        radius=0.05        # Radius in meters (5cm for face scans)
    )
    logger.info(f"After radius outlier removal: {len(pcd.points)}")
    
    return pcd


def create_mesh_from_point_cloud(pcd: o3d.geometry.PointCloud) -> o3d.geometry.TriangleMesh:
    """
    Create a watertight mesh from point cloud using Poisson surface reconstruction.
    """
    # Estimate normals (required for Poisson reconstruction)
    logger.info("Estimating normals...")
    pcd.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    pcd.orient_normals_consistent_tangent_plane(k=15)
    
    # Poisson surface reconstruction
    logger.info("Performing Poisson surface reconstruction...")
    mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, 
        depth=9,  # Depth of octree (higher = more detail, but slower)
        width=0,
        scale=1.1,
        linear_fit=False
    )
    
    logger.info(f"Mesh created with {len(mesh.vertices)} vertices and {len(mesh.triangles)} triangles")
    
    # Remove low-density vertices (noise)
    if len(densities) > 0:
        density_threshold = np.quantile(densities, 0.01)  # Remove bottom 1%
        vertices_to_remove = densities < density_threshold
        mesh.remove_vertices_by_mask(vertices_to_remove)
        logger.info(f"After density filtering: {len(mesh.vertices)} vertices")
    
    return mesh


def clean_mesh(mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
    """
    Clean and smooth the mesh.
    """
    # Remove degenerate triangles and non-manifold edges
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    
    # Smooth mesh to reduce noise
    logger.info("Smoothing mesh...")
    mesh = mesh.filter_smooth_simple(number_of_iterations=5)
    
    # Fill holes (small holes only)
    logger.info("Filling holes...")
    mesh.fill_holes()
    
    return mesh


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Mesh Cleanup API"}


@app.post("/clean-mesh")
async def clean_mesh_endpoint(
    file: UploadFile = File(...),
    return_format: Optional[str] = "ply"
):
    """
    Clean a PLY point cloud file and return a cleaned mesh.
    
    Parameters:
    - file: PLY point cloud file
    - return_format: Output format ("ply" or "obj")
    
    Returns:
    - Cleaned mesh file
    """
    if not file.filename.endswith('.ply'):
        raise HTTPException(status_code=400, detail="Only PLY files are supported")
    
    if return_format not in ['ply', 'obj']:
        raise HTTPException(status_code=400, detail="return_format must be 'ply' or 'obj'")
    
    # Create temporary files
    input_path = None
    output_path = None
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ply') as tmp_input:
            content = await file.read()
            tmp_input.write(content)
            input_path = tmp_input.name
        
        logger.info(f"Processing file: {file.filename}")
        
        # Load point cloud
        pcd = o3d.io.read_point_cloud(input_path)
        
        if len(pcd.points) == 0:
            raise HTTPException(status_code=400, detail="Point cloud is empty")
        
        logger.info(f"Loaded point cloud with {len(pcd.points)} points")
        
        # Clean point cloud
        pcd = clean_point_cloud(pcd)
        
        if len(pcd.points) < 1000:
            raise HTTPException(
                status_code=400, 
                detail=f"Too few points after cleaning ({len(pcd.points)}). Original scan may be too noisy."
            )
        
        # Create mesh from point cloud
        mesh = create_mesh_from_point_cloud(pcd)
        
        # Clean mesh
        mesh = clean_mesh(mesh)
        
        # Save cleaned mesh
        output_path = input_path.replace('.ply', f'_cleaned.{return_format}')
        
        if return_format == 'ply':
            o3d.io.write_triangle_mesh(output_path, mesh)
        else:  # obj
            o3d.io.write_triangle_mesh(output_path, mesh)
        
        logger.info(f"Cleaned mesh saved to {output_path}")
        
        # Return file
        return FileResponse(
            output_path,
            media_type='application/octet-stream',
            filename=f"{Path(file.filename).stem}_cleaned.{return_format}"
        )
        
    except Exception as e:
        logger.error(f"Error processing mesh: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing mesh: {str(e)}")
    
    finally:
        # Clean up temporary files
        if input_path and os.path.exists(input_path):
            os.unlink(input_path)
        # Note: output_path is returned to client, so we don't delete it immediately
        # In production, you might want to implement a cleanup job for old files


@app.post("/clean-point-cloud")
async def clean_point_cloud_endpoint(file: UploadFile = File(...)):
    """
    Clean a PLY point cloud file without creating a mesh.
    Returns cleaned point cloud as PLY.
    
    Useful if you want to keep it as a point cloud rather than mesh.
    """
    if not file.filename.endswith('.ply'):
        raise HTTPException(status_code=400, detail="Only PLY files are supported")
    
    input_path = None
    output_path = None
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ply') as tmp_input:
            content = await file.read()
            tmp_input.write(content)
            input_path = tmp_input.name
        
        logger.info(f"Processing point cloud: {file.filename}")
        
        # Load point cloud
        pcd = o3d.io.read_point_cloud(input_path)
        
        if len(pcd.points) == 0:
            raise HTTPException(status_code=400, detail="Point cloud is empty")
        
        # Clean point cloud
        pcd = clean_point_cloud(pcd)
        
        # Save cleaned point cloud
        output_path = input_path.replace('.ply', '_cleaned.ply')
        o3d.io.write_point_cloud(output_path, pcd)
        
        logger.info(f"Cleaned point cloud saved to {output_path}")
        
        # Return file
        return FileResponse(
            output_path,
            media_type='application/octet-stream',
            filename=f"{Path(file.filename).stem}_cleaned.ply"
        )
        
    except Exception as e:
        logger.error(f"Error processing point cloud: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing point cloud: {str(e)}")
    
    finally:
        if input_path and os.path.exists(input_path):
            os.unlink(input_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

