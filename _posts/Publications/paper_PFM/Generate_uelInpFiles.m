function Generate_uelInpFiles(kflag,crack_ratio,RHO,angle,suffix,step_length)
% kflag = 0; %1对应vertical，0对应horizontal
if kflag == 1
    str_position = 'vertical';
    remain_position = 'Horizontal';
else
    str_position = 'Horizontal';
    remain_position = 'vertical';
end
% crack_ratio = [0.01,0.05,0.1];
shape = 5;
%原始inp
% RHO = 10;
%random的Gc
MDGc = 1e-5;
% angle = 0;
% suffix = '_Nx6_Ny30.inp';
% suffix = '_Nx6_Ny10.inp';
% suffix = '_Nx6_Ny6.inp';
% suffix = '_Nx6_Ny6_preCrack.inp';
filename = ['R' num2str(RHO) 'D' num2str(angle) suffix];
% step_length=5e-7;
inputPath = cell(1, length(crack_ratio)); % 预分配 cell 数组存储路径
for i=1:length(crack_ratio)
    inputPath{i} = FUN_update_random_INP(filename, str_position, remain_position, crack_ratio(i),shape);
    FUN_randomInpToUEL(inputPath{i},step_length,MDGc)
    delete(inputPath{i})
end
delete(filename)
end