# Chapter 1: Project Overview

## 1.1 Executive Summary
PlantIntel AI is an end-to-end artificial intelligence decision-support platform designed for high-precision plant disease classification, disease severity quantification, and visual explainability. The platform integrates a modern lightweight neural network architecture (EfficientNetV2-S) augmented with an Adaptive Lightweight Attention (ALA) mechanism.

## 1.2 Problem Statement
Global crop losses caused by phytopathogens threaten food security. Rapid identification and severity assessment are critical for targeted treatment. Current deep learning solutions often lack interpretability, making field adoption by agronomists challenging.

## 1.3 Key Innovations
1. **Adaptive Lightweight Attention:** Dual-stage channel and spatial attention with dynamic gating parameters requiring minimal parameter overhead (+0.38%).
2. **Dual Visual Explainability:** Co-registration of Grad-CAM++ feature gradients with attention spatial weight maps.
3. **Automated Quality Control:** Pre-inference image validation to filter corrupt, blurry, or non-botanical inputs.
4. **Production-Grade Infrastructure:** Full persistent web application with automated PDF and CSV diagnostic export capabilities.
