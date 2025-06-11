#! /user/bin/python
# -*- coding:UTF-8 -*-
from abaqus import *
from abaqusConstants import *
from odbAccess import openOdb
from caeModules import *
from driverUtils import executeOnCaeStartup
import os
#主程序:功能：获取当前目录指定后缀的所有odb中力位移曲线，并输出到txt中
#----------------------------功能0：获取当前目录----------------------------------------
current_directory = os.getcwd()
#指定后缀
endwith = '_UE'
#----------------------------功能1：获取目录中的所有.inp 文件(这里需要找到后缀是_UE.inp)-------------
inp_files = [file for file in os.listdir(current_directory) if file.endswith(endwith+'.inp')]
file_names=[]
for inp_file in inp_files:
	#将所在文件目录和文件名连接起来成为一个完整的路径
    input_file_path = os.path.join(current_directory, inp_file)
    #添加自动收集相关inp名字的指令
    file_name = os.path.splitext(os.path.basename(input_file_path))[0]
    file_names.append(file_name)

#---------------------------功能2：获取指定node number和处理odb文件输出位移-力曲线-------------
node_set_name = 'RP'
for name in file_names:
    # 构建 .inp 和 .odb 文件路径
    input_file_path = os.path.join(current_directory, name + '.inp')  # 使用os.path.join更安全
    base_path = os.path.join(current_directory, name + '.odb')
    #----------------------功能2.1：获取整个模型的尺寸，用于计算应力应变曲线--------------
    # 打开 ODB 文件
    odb = openOdb(path=base_path)
    # 获取第一个实例（通常情况下只有一个实例）
    instance = odb.rootAssembly.instances.values()[0]
    # 初始化尺寸变量
    minX = minY = minZ = maxX = maxY = maxZ = None
    # 遍历所有节点获取几何范围
    for node in instance.nodes:
        coordinates = node.coordinates
        x, y, z = coordinates
        if minX is None or x < minX:
            minX = x
        if minY is None or y < minY:
            minY = y
        if minZ is None or z < minZ:
            minZ = z
        if maxX is None or x > maxX:
            maxX = x
        if maxY is None or y > maxY:
            maxY = y
        if maxZ is None or z > maxZ:
            maxZ = z
    minX = float(minX)
    minY = float(minY)
    minZ = float(minZ)
    maxX = float(maxX)
    maxY = float(maxY)
    maxZ = float(maxZ)
    # 处理 .odb 文件
    odb = session.odbs[base_path]
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    # 提取节点标签
    #在odb中获取历史输出变量的节点信息
    S = odb.steps['Step-1']
    R = S.historyRegions
    R_value = R.keys()#这里的R_value = ['Node PART-1-1.7918']
    # 从列表中取出字符串
    node_string = R_value[0]
    # 通过'.'进行分割，得到一个包含多个元素的列表
    split_values = node_string.split('.')
    # 取出列表中最后一个元素，并将其转换为整数类型
    load_node_label = str(int(split_values[-1]))
    # 创建 RF 和 U 数据对象
    xy1 = xyPlot.XYDataFromHistory(odb=odb, 
        outputVariableName='Reaction force: RF2 at Node ' + load_node_label + ' in NSET '+node_set_name, 
        steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
    session.xyDataObjects.changeKey(xy1.name, name + '_RF')
    xy2 = xyPlot.XYDataFromHistory(odb=odb, 
        outputVariableName='Spatial displacement: U2 at Node ' + load_node_label + ' in NSET '+node_set_name, 
        steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
    session.xyDataObjects.changeKey(xy2.name, name + '_U')
    # 组合 RF 和 U 数据对象
    c1 = session.xyDataObjects[name + '_U']
    c2 = session.xyDataObjects[name + '_RF']
    xy3 = combine(c1/maxY, c2/maxX)
    xy3_name = name + '_S-E'  
    session.xyDataObjects.changeKey(xy3.name, xy3_name)  
    #--------------------------------功能3：将位移-力曲线写入数据到文本文件，待处理（这里可以直接从xydata中写入，不需要经过xyplot）------------------------
    # 获取 xy 数据对象
    xy3 = session.xyDataObjects[name+'_S-E']
    # 将 xy 数据对象写入文本文件
    # 将 xy 数据对象写入文本文件
    session.writeXYReport(fileName=name+'_S-E'+'.txt', xyData=(xy3, ))