# -*- coding: utf-8 -*-
# 文件名不要有空格
# 可直接在command中：abaqus cae nogui=1_modeling.py
# 注意meshNumber的设定
#from Function_modeling import Fun_random_base_modeling_INPs #完整模型
from Function_modeling_precrack import Fun_random_base_modeling_INPs #包含precrack模型
# Example usage
meshNumber = 8
modulus_random = 1.0
modulus_matrix = 106.0
RHO_P = 10
NNx = 6
NNy = 6
#angles = list(range(1, 10, 2))
angles = [0]
originalName = 'R' + str(RHO_P) + 'D{}'
#baseName = 'R' + str(RHO_P) + 'D{}' + '_Nx' + str(NNx) + '_Ny' + str(NNy)
baseName_precrack = 'R' + str(RHO_P) + 'D{}' + '_Nx' + str(NNx) + '_Ny' + str(NNy)+'_preCrack'
NEWNAMES = []
for angle_value in angles:
    originalNames = originalName.format(angle_value)
    #angleS = baseName.format(angle_value)  # 创建nameS
    angleS = baseName_precrack.format(angle_value)  # 创建nameS,含preCrack
    NEWNAMES.append(angleS)
    # 创建模型
    Fun_random_base_modeling_INPs(angle_degrees=angle_value, RHO_P=RHO_P, NNx=NNx, NNy=NNy, NEW_NAME=angleS, modelName=originalNames,meshNumber=meshNumber, modulus_random = modulus_random, modulus_matrix = modulus_matrix)
