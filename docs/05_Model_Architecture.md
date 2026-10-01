# Chapter 5: Model Architecture

## 5.1 EfficientNetV2-S Backbone
EfficientNetV2-S utilizes Fused-MBConv blocks in early stages and MBConv blocks in later stages with progressive learning strategies.

- **Baseline Input:** `(3, 224, 224)`
- **Feature Maps Output:** `(1280, 7, 7)`
- **Baseline Classification Head:** Dropout (0.2) + Linear (1280 -> 38 classes).
- **Baseline Parameters:** 21,458,488.
