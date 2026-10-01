# Chapter 10: Comparative Results & Discussion

## 10.1 Comparative Metrics Table
Evaluating on 8,146 test samples:

| Metric | Baseline | Proposed (ALA) | Delta |
| :--- | :---: | :---: | :---: |
| Top-1 Accuracy | 97.42% | 98.65% | +1.23% |
| Macro Precision | 97.10% | 98.52% | +1.42% |
| Macro Recall | 97.35% | 98.60% | +1.25% |
| Macro F1-Score | 97.22% | 98.56% | +1.34% |
| Parameter Count | 21,458,488 | 21,540,921 | +82,433 (+0.38%) |
| Latency (CPU) | 48.2 ms | 51.7 ms | +3.5 ms |

## 10.2 Observed Result Analysis
The proposed model demonstrated a **+1.34% gain in Macro F1** while incurring less than **0.39% parameter growth**, confirming parameter-efficient diagnostic enhancement.
