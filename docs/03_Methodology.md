# Chapter 3: Methodology

## 3.1 Research Framework
The research methodology enforces strict scientific controls to validate the performance gains of the proposed architecture:
1. **Identical Splitting:** Both baseline and proposed models are trained and evaluated on identical train/validation/test partitions.
2. **Reproducibility:** Seed initialization (`SEED=42`) across Python, NumPy, and PyTorch.
3. **Parameter Efficiency:** Metric gains are evaluated relative to added parameters and computational latency.

## 3.2 Evaluation Protocol
- **Metrics:** Top-1 Accuracy, Macro-averaged Precision, Recall, F1-Score, and Inference Latency.
- **Verification:** All metrics are programmatically computed on held-out test data (`8,146` samples).
