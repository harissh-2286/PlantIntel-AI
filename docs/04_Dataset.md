# Chapter 4: Dataset Analysis & Preprocessing

## 4.1 Corpus Description
The dataset comprises 54,303 leaf images across 38 class categories representing 14 plant species and various fungal, bacterial, and viral disease pathotypes.

## 4.2 Data Partitioning
- **Train Split:** 38,012 images (70%)
- **Validation Split:** 8,145 images (15%)
- **Test Split:** 8,146 images (15%)

## 4.3 Data Leakage Audit
- Binary SHA-256 hash check confirmed zero overlapping images across train, validation, and test splits.
- On-the-fly augmentation prevents stored duplicate leakage.
