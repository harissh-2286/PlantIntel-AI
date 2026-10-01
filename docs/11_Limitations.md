# Chapter 11: System Limitations

## 11.1 Key Limitations
1. **Lighting & Background Sensitivity:** Specular highlights or direct solar glare on leaves may affect severity thresholding.
2. **Surface Area vs. Volumetric Depth:** Severity estimation measures visible affected surface percentage rather than 3D canopy penetration.
3. **Hardware Latency Bounds:** CPU inference requires ~51.7 ms, suitable for cloud web APIs but requiring quantization for ultra-low latency microcontrollers.
