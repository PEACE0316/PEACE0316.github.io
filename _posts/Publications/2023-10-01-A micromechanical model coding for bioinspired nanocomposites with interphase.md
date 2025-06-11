---
layout: post/Publications
title: A micromechanical model coding for bioinspired nanocomposites with interphase
categories: Publication
description: 將發表的文章中使用的coding封裝和記錄下來以便使用和查找
keywords: interphase，matlab
---


# A micromechanical model coding for bioinspired nanocomposites with interphase

- _如感興趣，請參考作者的原始文章 https://doi.org/10.1016/j.compstruct.2023.117316_
---

## 3. Matlab coding
### 3.1 calculate effective modulus with interphase
```matlab
clc, clear
% 固定參數
[Em, Ep, hp, rho, delta_L, m] = deal(1, 400, 1, 12.4/4.8, 3/3.1, 0.5/400);
[Gm, Gi] = deal(Em/2.6, (m*Ep)/2.6);
k1 = 4/3; h = 2.4;

% 計算中間變量
hi = (k1-1)*hp; 
h_pi = hp + hi;
L = rho*h*delta_L;
l1 = rho*h*(1-delta_L);

% 材料參數矩陣
E = [Ep, m*Ep, Em];
G = [NaN, Gi, Gm]; % E1無剪切模量

% 核心計算
A1 = E(2)*hi^2*(5*hi + 3*(h-2*h_pi) + 3*hp) / (G(2)*6*(h-hp));
A2 = E(3)*(h-h_pi)^3 / (G(3)*3*(h-hp));
A3 = E(3)/G(2)*(hi - hi^2/(2*(2*hi + (h-2*h_pi) + hp))) * (h-h_pi);

avg_E = (E(1)*hp + E(2)*hi + E(3)*(h-h_pi)) / h;
alpha1 = sqrt(2*G(3)/(E(1)*hp*(2*hi*G(3)/G(2) + (h-2*h_pi))));
alpha2 = sqrt(avg_E/E(1)/(A1+A2+A3));

beta1 = alpha1*(L-l1);
beta2 = alpha2*l1;

% 等效模量計算
delta_P = 2*hp/h;
avg_EI = (E(1)*hp + E(2)*hi + E(3)*(h-2*h_pi)) / h;
avg_EII = 2*(E(1)*hp + E(2)*hi) / h;

term1 = E(1)*(1-0.5*delta_P)*0.5*delta_P/(2*G(2)*rho^2);
term2 = (E(1)/2/G(3)-E(1)/2/G(2))*(1-0.5*k1*delta_P)^2*0.5*delta_P/(rho^2*(1-0.5*delta_P));
Ec_inv = 2*(1-delta_L)/avg_EI + (2*delta_L-1)/avg_EII + ...
         (1/avg_EI - 1/avg_EII) * (term1 + term2 - 2*(1-delta_L)^2/beta2^2) / ...
         ((2*delta_L-1)*tanh(beta1/2)/beta1 + (1-delta_L)/(beta2*tanh(beta2)));

Ec = Ec_inv^(-1);
