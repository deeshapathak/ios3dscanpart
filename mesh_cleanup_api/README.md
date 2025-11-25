# Mesh Cleanup API

FastAPI backend for cleaning and processing PLY point cloud files from TrueDepth camera scans. Optimized for face/rhinoplasty scans.

## Features

- **Point Cloud Denoising**: Removes statistical and radius outliers
- **Mesh Generation**: Creates watertight mesh using Poisson surface reconstruction
- **Mesh Cleaning**: Smooths surface and fills holes
- **Optimized for Face Scans**: Parameters tuned for TrueDepth camera face scans

## Setup

### Prerequisites

**Important:** Open3D requires Python 3.10 or 3.11. Python 3.12+ is not yet supported.

If you have Python 3.13+, you have two options:

1. **Use Docker** (Recommended):
   ```bash
   docker build -t mesh-cleanup-api .
   docker run -p 8000:8000 mesh-cleanup-api
   ```

2. **Install Python 3.11**:
   ```bash
   # macOS
   brew install python@3.11
   python3.11 -m pip install -r requirements.txt
   python3.11 main.py
   ```

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If you get an error about open3d, make sure you're using Python 3.10 or 3.11.

### 2. Run the Server

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST `/clean-mesh`

Cleans a PLY point cloud and returns a cleaned mesh.

**Parameters:**
- `file`: PLY file (multipart/form-data)
- `return_format`: Optional, "ply" or "obj" (default: "ply")

**Example:**
```bash
curl -X POST "http://localhost:8000/clean-mesh?return_format=ply" \
  -F "file=@scan.ply"
```

### POST `/clean-point-cloud`

Cleans a PLY point cloud without creating a mesh. Returns cleaned point cloud.

**Parameters:**
- `file`: PLY file (multipart/form-data)

**Example:**
```bash
curl -X POST "http://localhost:8000/clean-point-cloud" \
  -F "file=@scan.ply"
```

### GET `/`

Health check endpoint.

## Processing Pipeline

1. **Statistical Outlier Removal**: Removes points far from neighbors
2. **Radius Outlier Removal**: Removes isolated points
3. **Normal Estimation**: Required for mesh generation
4. **Poisson Surface Reconstruction**: Creates watertight mesh
5. **Density-based Cleaning**: Removes low-density vertices (noise)
6. **Mesh Smoothing**: Smooths surface
7. **Hole Filling**: Fills small holes

## iOS Integration

### Swift Example

```swift
func uploadPLYFile(url: URL) async throws -> URL {
    let boundary = UUID().uuidString
    var request = URLRequest(url: URL(string: "http://your-server:8000/clean-mesh?return_format=ply")!)
    request.httpMethod = "POST"
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
    
    var body = Data()
    
    // Add file
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"scan.ply\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
    body.append(try Data(contentsOf: url))
    body.append("\r\n".data(using: .utf8)!)
    body.append("--\(boundary)--\r\n".data(using: .utf8)!)
    
    request.httpBody = body
    
    let (data, response) = try await URLSession.shared.data(for: request)
    
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NSError(domain: "APIError", code: -1)
    }
    
    // Save cleaned mesh
    let outputURL = FileManager.default.temporaryDirectory.appendingPathComponent("cleaned_mesh.ply")
    try data.write(to: outputURL)
    return outputURL
}
```

## Deployment

### Local Development
```bash
uvicorn main:app --reload
```

### Production (with Docker)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t mesh-cleanup-api .
docker run -p 8000:8000 mesh-cleanup-api
```

### Cloud Deployment

**AWS Lambda** (with serverless framework)
**Google Cloud Run**
**Heroku**
**DigitalOcean App Platform**

## Configuration

You can adjust processing parameters in `main.py`:

- `nb_neighbors`: Number of neighbors for statistical outlier removal (default: 20)
- `std_ratio`: Standard deviation ratio threshold (default: 2.0)
- `radius`: Radius for radius outlier removal in meters (default: 0.05)
- `depth`: Poisson reconstruction depth (default: 9, higher = more detail)
- `smoothing_iterations`: Number of smoothing iterations (default: 5)

## Notes

- Point clouds with fewer than 1000 points after cleaning will be rejected
- Processing time depends on point cloud size (typically 5-30 seconds)
- For medical/rhinoplasty use, ensure HIPAA compliance if handling patient data

