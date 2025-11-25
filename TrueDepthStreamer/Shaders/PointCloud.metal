/*
See LICENSE folder for this sample’s licensing information.

Abstract:
Metal shaders used for point-cloud view
*/

#include <metal_stdlib>
using namespace metal;

typedef struct
{
    float4 clipSpacePosition [[position]];
    float2 coor;
    float pSize [[point_size]];
    float depth;
    float4 color;
} RasterizerDataColor;

// Vertex Function
vertex RasterizerDataColor
vertexShaderPoints(uint vertexID [[ vertex_id ]],
                   texture2d<float, access::read> depthTexture [[ texture(0) ]],
                   constant float4x4& viewMatrix [[ buffer(0) ]],
                   constant float3x3& cameraIntrinsics [[ buffer(1) ]])
{
    RasterizerDataColor out;
    
    uint2 pos;
    pos.y = vertexID / depthTexture.get_width();
    pos.x = vertexID % depthTexture.get_width();
    
    // depthDataType is kCVPixelFormatType_DepthFloat16
    float rawDepth = depthTexture.read(pos).x;
    float depth = rawDepth * 1000.0f;  // Convert to millimeters
    
    // Skip invalid depths (0 or too far)
    if (rawDepth <= 0.0 || rawDepth >= 5.0) {
        // Position invalid points far away so they get clipped
        out.clipSpacePosition = float4(0, 0, 10000, 1);
        out.depth = 0.0;
        out.pSize = 0.0;
        return out;
    }
    
    float xrw = (pos.x - cameraIntrinsics[2][0]) * depth / cameraIntrinsics[0][0];
    float yrw = (pos.y - cameraIntrinsics[2][1]) * depth / cameraIntrinsics[1][1];
    
    float4 xyzw = { xrw, yrw, depth, 1.f };
    
    out.clipSpacePosition = viewMatrix * xyzw;
    // Normalize texture coordinates to [0, 1] range
    out.coor = { pos.x / (depthTexture.get_width() - 1.0f), pos.y / (depthTexture.get_height() - 1.0f) };
    out.depth = depth;
    out.pSize = 5.0f;
    
    return out;
}

fragment float4 fragmentShaderPoints(RasterizerDataColor in [[stage_in]],
                                     texture2d<float> colorTexture [[ texture(0) ]])
{
    // Only render valid depth points (depth > 0 and reasonable range)
    if (in.depth > 0.0 && in.depth < 5000.0) {
        constexpr sampler textureSampler (mag_filter::linear, min_filter::linear);
        // Clamp texture coordinates to valid range
        float2 clampedCoord = clamp(in.coor, 0.0, 1.0);
        const float4 colorSample = colorTexture.sample(textureSampler, clampedCoord);
        
        // Return color if valid, otherwise discard
        if (colorSample.a > 0.0) {
            return colorSample;
        }
    }
    discard_fragment();
    return float4(0, 0, 0, 0);
}


