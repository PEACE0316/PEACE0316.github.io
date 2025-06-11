%% run the python script in the matlab as well
%% ! Heping XIA (heping_xia@hotmail.com)

%% First step
!abaqus cae noGUI=1_modeling.py
disp('>>> The target inp files are established')

%% Second step
kflag = 0; %1对应vertical，0对应horizontal
crack_ratio = [0.01];
RHO = 10;
angle = 0;
suffix = '_Nx6_Ny6_preCrack.inp';
step_length=5e-7;
Generate_uelInpFiles(kflag,crack_ratio,RHO,angle,suffix,step_length);
disp('>>> The target uelInp files are established')

%% Third step
!abaqus script=process_bat.py
!abaqus script=resume_bat.py
!abaqus script=suspend_bat.py
!abaqus script=terminate_bat.py
disp('>>> Bat files established')

%% Last step
!run.bat