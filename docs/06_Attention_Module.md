# Chapter 6: Adaptive Lightweight Attention Module

## 6.1 Mathematical Formulation
The Adaptive Lightweight Attention (ALA) module integrates channel and spatial attention maps via learnable gating factors $\alpha$ and $\beta$:

$$F_{channel} = \sigma(W_1(\delta(W_0(AvgPool(F)))) + W_1(\delta(W_0(MaxPool(F)))))$$
$$F_{spatial} = \sigma(Conv_{7x7}([AvgPool(F'); MaxPool(F')])$$
$$F_{out} = \alpha \cdot (F \odot F_{channel}) + \beta \cdot (F \odot F_{spatial})$$

Where $\sigma$ is Sigmoid, $\delta$ is ReLU, and $\alpha, \beta$ are initial learnable weights initialized to 0.5.

## 6.2 Parameter Efficiency
- **Channel Attention Params:** 82,432
- **Spatial Attention Params:** 98
- **Gating Parameters:** 2
- **Total Attention Params:** 82,433 (+0.38% over baseline)
