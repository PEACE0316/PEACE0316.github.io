% for average tensile stress and shear stress with respect to interphase
% 求平均应力，需要将该部分的应力分布函数表达出来，也就是需要将D1,D3写出来，并代入计算(具体表达式见原文)
clc,clear
syms x y SSa 
%% 输入参数
m = 0.001;
Ep = 120;
Ei = m*Ep;
Em = 0.1; %GPa
Gi = Ei/2.6;Gm = Em/2.6;  %GPa
hp = 3; hi = 0.9; 
% Hm = 6;
h = 10;
Hm = h-2*(hp+hi);  %nm
h_pi = hp+hi;
sigma_a = 0.01;
SSa = sigma_a*(2*h_pi+Hm);       %GPa*nm
rho =0:(100-0)/300:100;
LL = rho*h;
delta_L = 0.9;
alpha_1 = sqrt(2*Gm/(Ep*hp*(2*hi*Gm/Gi+Hm)));
avg_E = (Ep*hp+Ei*hi+Em*(h_pi+Hm))/hp;
A_1 = Ei*(hi^2*(5*hi+3*Hm+3*hp))/Gi/(6*(2*hi+Hm+hp));
A_2 = Em*(hi+Hm+hp)^3/Gm/(3*(2*hi+Hm+hp));
A_3 = Em/Gi*(hi-hi^2/(2*(2*hi+Hm+hp)))*(h_pi+Hm);
A_4 = Em/Gi*(hi-hi^2/2/(2*hi+Hm+hp))+Em/Gm*(hi+Hm+hp)^2/(2*(2*hi+Hm+hp));
alpha_2 = sqrt(avg_E/Ep/(A_1+A_2+A_3));

A = SSa*Ep/avg_E/hp-SSa/2/(hp+Ei*hi/Ep);
avg_EI = (Ep*hp+Ei*hi+Em*(h-2*h_pi))/h;
avg_EII = (2*Ep*hp+2*Ei*hi+Em*Hm)/h;
for i = 1:length(rho)
    L(i) = delta_L*LL(i);
    l1(i) = (1-delta_L)*LL(i);
    rho_p(i) = L(i)/hp;
    beta_1(i) = alpha_1.*(L(i)-l1(i));
    beta_2(i) = alpha_2.*l1(i);
    D1(i) = A/(-2*sinh(alpha_1.*(L(i)-l1(i))./2)-2*alpha_1*cosh(alpha_1.*(L(i)-l1(i))./2)./alpha_2./tanh(alpha_2.*l1(i))); %%为负值
    D3(i) = A/((-2*alpha_2*sinh(alpha_2.*l1(i))*tanh(alpha_1.*(L(i)-l1(i))/2))/alpha_1-2.*cosh(alpha_2.*l1(i)));
    % interphase 部分正应力分两个区域
    %区域I
    SP1_I(i) = 2.*D3(i).*cosh(alpha_2*x)+Ep*sigma_a/avg_EI; %%platelet在区域I的正应力
    TI11_I(i) = -hp.*diff(SP1_I(i),x);
    SI1_Ix(i) = Ei/Ep.*SP1_I(i)*hi+A_1.*diff(TI11_I(i),x);%单个interphase的任意x处的合正应力
    TI11_Ix(i) = -hp.*diff(SP1_I(i),x)*hi;%单个interphase的任意x处的合剪应力
    SI1_Ixall(i) = double(int(SI1_Ix(i),0,l1(i)));
    TI11_Ixall(i) = double(int(TI11_Ix(i),0,l1(i)));
    %区域II
    SP1(i) = 2.*D1(i)*sinh(alpha_1*x)+Ep*sigma_a/avg_EII;
    TI11(i) = -hp*diff(SP1(i),x);
    SI1x(i) = Ei/Ep.*SP1(i).*hi+Ei*hi^2/(2*Gi).*diff(TI11(i),x);%单个interphase的任意x处的合正应力
    TI11x(i) = -hp.*diff(SP1(i),x)*hi;%单个interphase的任意x处的合剪应力
    SI1xall(i) = double(int(SI1x(i),-(L(i)-l1(i))/2,(L(i)-l1(i))/2));
    TI11xall(i) = double(int(TI11x(i),-(L(i)-l1(i))/2,(L(i)-l1(i))/2));
    avgS(i) = (SI1_Ixall(i)+SI1xall(i))./L(i)/sigma_a;
    avgT(i) = (TI11_Ixall(i)+TI11xall(i))./L(i)/sigma_a;
end
% plot(rho,avgS)
% hold on
plot(rho,avgT)
hold on
