# Chapter 7: Disease Severity Estimation

## 7.1 Severity Estimation Engine
Disease severity is estimated as an affected leaf tissue percentage without requiring manual pixel-level mask annotations:

1. **Leaf Surface Isolation:** Otsu thresholding in LAB color space (a* and b* channels) to segment plant tissue from background.
2. **Lesion Detection:** Color variance extraction in HSV color space (Hue < 35 or Saturation/Value anomalies).
3. **Morphological Cleanup:** Morphological opening and connected components analysis (CC_STAT_AREA >= 15px) to filter sensor noise.
4. **Ratio Computation:** $\text{Severity \%} = \min\left(100.0, \frac{\text{Lesion Pixels}}{\text{Leaf Surface Pixels}} \times 100\right)$

## 7.2 Severity Categorization Thresholds
- **0 - 5%:** Minimal
- **> 5 - 20%:** Mild
- **> 20 - 40%:** Moderate
- **> 40 - 60%:** Severe
- **> 60%:** Very Severe
