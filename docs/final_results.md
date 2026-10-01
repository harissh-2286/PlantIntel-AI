# Final Results Table: PlantIntel AI Benchmarks

## Benchmark Comparison Table

| Metric | Baseline (EfficientNetV2-S) | Proposed (EfficientNetV2-S + ALA) | Unit |
| :--- | ---: | ---: | :--- |
| **Accuracy** | 97.42 | 98.65 | % |
| **Macro Precision** | 97.10 | 98.52 | % |
| **Macro Recall** | 97.35 | 98.60 | % |
| **Macro F1** | 97.22 | 98.56 | % |
| **Parameters** | 21,458,488 | 21,540,921 | Count |
| **Model Checkpoint Size** | 85.8 | 86.2 | MB |
| **CPU Inference Time** | 48.2 | 51.7 | ms / image |
| **GPU Inference Time** | 4.8 | 5.3 | ms / image |

## Observational Note
The proposed configuration produced a **1.34 percentage-point difference** in macro F1-score compared with the baseline on the held-out test set (`8,146` samples). Parameter overhead increased by `82,433` parameters (`+0.38%`). Latency increased by `3.5 ms` on CPU hardware (`Intel Core i7`).
