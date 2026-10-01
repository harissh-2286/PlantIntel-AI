# Chapter 8: Explainable AI (XAI) Framework

## 8.1 Grad-CAM++ Integration
Grad-CAM++ generates fine-grained class activation maps using higher-order partial derivatives of score $Y^c$ with respect to feature map $A^k$:

$$w_k^c = \sum_i \sum_j \alpha_{ij}^{kc} \cdot \text{relu}\left(\frac{\partial Y^c}{\partial A_{ij}^k}\right)$$
$$L_{\text{Grad-CAM++}}^c = \text{relu}\left(\sum_k w_k^c A^k\right)$$

## 8.2 Co-Registration with Adaptive Attention
The system computes both Grad-CAM++ gradients and spatial attention weights $\sigma(Conv_{7x7}(\cdot))$, presenting side-by-side overlays in the UI for holistic diagnostic verification.
