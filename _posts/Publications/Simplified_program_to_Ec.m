%% 具体表达式参考原文
clc,clear
% 预设参数
Em = 1; %GPa 控制不变
Ep = 400; %GPa 控制不变
Gm = Em/2.6;  %GPa 控制不变
hp = 1; % 控制不变 platelet half thickness
k1 = 4/3; % thickness ratio hi/hp+1
hi = (k1-1)*hp; % interphase thickness
h_pi = hp+hi; 
h = 2.4; % UC thickness
y_1 = hp;
y_5 = h;
y_2 = hp+hi;
m = 0.5/400; % Ei/Ep
rho = 12.4/4.8;  % RVE aspect ratio
LL = rho*h;  % RVE长度
delta_L = 3/3.1; % platelet length ratio
for i = 1:length(k1)
L = LL*delta_L;
l1 = LL*(1-delta_L);
rho_p = L/hp;
Ei = m.*Ep;
Gi = Ei./2.6;
delta_P = 2*hp/h;

E1 = Ep;
E2 = Ei;
E3 = Em;
G2 = Gi;
G3 = Gm;

A_1(i) = Ei.*(hi(i).^2*(5*hi(i)+3*(h-2*h_pi(i))+3*hp))./Gi./(6*(h-hp));
A_3(i) = Em./Gi.*(hi(i)-hi(i).^2/(2*(2*hi(i)+(h-2*h_pi(i))+hp)))*(h-h_pi(i));
A_2(i) = Em.*(h-h_pi(i)).^3/Gm./(3.*(h-hp));
avg_E(i) = (Ep*hp+Ei.*hi(i)+Em*(h-h_pi(i)))./hp;
alpha_1(i) = sqrt(2*Gm./(Ep*hp.*(2*hi(i)*Gm./Gi+(h-2*h_pi(i)))));

alpha_2(i) = sqrt(avg_E(i)./Ep./(A_1(i)+A_2(i)+A_3(i)));
beta_1(i) = alpha_1(i).*(L-l1);
beta_2(i) = alpha_2(i).*l1;
avg_EI(i) = (E1*hp+Ei*hi(i)+Em*(h-2*h_pi(i)))/h;
avg_EII(i) = 2*(E1*hp+Ei*hi(i))/h;

Ecinv(i) = 2.*(1-delta_L)./avg_EI(i)+(2*delta_L-1)./avg_EII(i)+(1./avg_EI(i)-1./avg_EII(i)).*((E1*(1-0.5*delta_P)*(0.5*delta_P)./2./G2./rho.^2+(E1/2/G3-E1/2/G2).*(1-0.5*k1(i)*delta_P).^2*(0.5*delta_P)./rho.^2/(1-0.5*delta_P))-2*(1-delta_L).^2./beta_2(i).^2)./((2*delta_L-1).*tanh(beta_1(i)./2)./beta_1(i)+(1-delta_L)./beta_2(i)./tanh(beta_2(i)));
Ec(i) = Ecinv(i).^(-1); %% Ec的求解表达式
end
