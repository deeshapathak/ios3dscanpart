"""
Simple test script for the mesh cleanup API.
"""

import requests
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    response = requests.get(f"{API_URL}/")
    print(f"Health check: {response.json()}")
    assert response.status_code == 200

def test_clean_mesh(ply_file_path: str):
    """Test mesh cleaning endpoint."""
    print(f"\nTesting mesh cleaning with file: {ply_file_path}")
    
    with open(ply_file_path, 'rb') as f:
        files = {'file': (ply_file_path, f, 'application/octet-stream')}
        response = requests.post(
            f"{API_URL}/clean-mesh?return_format=ply",
            files=files
        )
    
    if response.status_code == 200:
        output_path = ply_file_path.replace('.ply', '_cleaned.ply')
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ Cleaned mesh saved to: {output_path}")
        print(f"  Response size: {len(response.content)} bytes")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <path_to_ply_file>")
        sys.exit(1)
    
    ply_file = sys.argv[1]
    
    try:
        test_health()
        test_clean_mesh(ply_file)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
        sys.exit(1)

