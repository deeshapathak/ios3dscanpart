//
//  MeshCleanupService.swift
//  TrueDepthStreamer
//
//  Helper class for uploading PLY files to mesh cleanup API
//

import Foundation

class MeshCleanupService {
    let baseURL: String
    
    init(baseURL: String = "http://localhost:8000") {
        self.baseURL = baseURL
    }
    
    /// Upload PLY file to mesh cleanup API and get cleaned mesh
    /// - Parameters:
    ///   - plyURL: Local file URL of PLY file
    ///   - returnFormat: Output format ("ply" or "obj")
    /// - Returns: URL of cleaned mesh file
    func cleanMesh(plyURL: URL, returnFormat: String = "ply") async throws -> URL {
        let url = URL(string: "\(baseURL)/clean-mesh?return_format=\(returnFormat)")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add file
        let filename = plyURL.lastPathComponent
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
        body.append(try Data(contentsOf: plyURL))
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw MeshCleanupError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw MeshCleanupError.apiError(statusCode: httpResponse.statusCode, message: errorMessage)
        }
        
        // Save cleaned mesh to temporary directory
        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("cleaned_mesh.\(returnFormat)")
        try data.write(to: outputURL)
        
        return outputURL
    }
    
    /// Clean point cloud without creating mesh
    /// - Parameter plyURL: Local file URL of PLY file
    /// - Returns: URL of cleaned point cloud file
    func cleanPointCloud(plyURL: URL) async throws -> URL {
        let url = URL(string: "\(baseURL)/clean-point-cloud")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // Add file
        let filename = plyURL.lastPathComponent
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"\(filename)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
        body.append(try Data(contentsOf: plyURL))
        body.append("\r\n".data(using: .utf8)!)
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw MeshCleanupError.invalidResponse
        }
        
        guard httpResponse.statusCode == 200 else {
            let errorMessage = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw MeshCleanupError.apiError(statusCode: httpResponse.statusCode, message: errorMessage)
        }
        
        // Save cleaned point cloud
        let outputURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("cleaned_pointcloud.ply")
        try data.write(to: outputURL)
        
        return outputURL
    }
    
    /// Check if API is available
    func checkHealth() async throws -> Bool {
        let url = URL(string: "\(baseURL)/")!
        let (_, response) = try await URLSession.shared.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            return false
        }
        
        return httpResponse.statusCode == 200
    }
}

enum MeshCleanupError: LocalizedError {
    case invalidResponse
    case apiError(statusCode: Int, message: String)
    case fileNotFound
    case networkError(Error)
    
    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Invalid response from server"
        case .apiError(let statusCode, let message):
            return "API error (\(statusCode)): \(message)"
        case .fileNotFound:
            return "PLY file not found"
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        }
    }
}

// MARK: - Usage Example
/*
 
 // In your CameraViewController or wherever you save the PLY:
 
 let cleanupService = MeshCleanupService(baseURL: "http://your-server:8000")
 
 Task {
     do {
         // Get the saved PLY file URL
         guard let plyURL = getSavedPLYFileURL() else { return }
         
         // Show loading indicator
         showLoadingIndicator()
         
         // Clean the mesh
         let cleanedMeshURL = try await cleanupService.cleanMesh(plyURL: plyURL, returnFormat: "ply")
         
         // Hide loading indicator
         hideLoadingIndicator()
         
         // Use the cleaned mesh
         print("Cleaned mesh saved to: \(cleanedMeshURL)")
         
         // Optionally, copy to Documents directory
         let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
         let finalURL = documentsURL.appendingPathComponent("cleaned_mesh.ply")
         try? FileManager.default.copyItem(at: cleanedMeshURL, to: finalURL)
         
     } catch {
         hideLoadingIndicator()
         showError("Failed to clean mesh: \(error.localizedDescription)")
     }
 }
 
 */

