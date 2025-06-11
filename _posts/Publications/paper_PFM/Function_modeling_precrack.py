# -*- coding:UTF-8 -*-
# 这个.py是最新的版本,先建立large_model的base
#2024/9/28
def Fun_random_base_modeling_INPs(angle_degrees, RHO_P, NNx, NNy, NEW_NAME, modelName, meshNumber,modulus_random,modulus_matrix):
    from abaqus import mdb
    import random
    from abaqus import *
    from abaqusConstants import *
    from caeModules import *
    import math
    import numpy as np
    import os
    # -----------------------------------------FLAG-------------------------------------------------
    kPBC = 0  # 0表示没有用PBC,1表示用PBC
    session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
    # --------------------------------------STEP1:建立RVE模型------------------------------------------
    # 创建新模型
    modelName = "BM"
    MyModel = mdb.Model(name=modelName)
    Nx = 1
    Ny = 1
    #modulus_random = 1.0
    #modulus_matrix = 2800.0
    # =====================================1.1 分别建立单个platelet=====================================
    # 用于参数修改（单位是um）
    #angle_degrees = 0
    #RHO_P = 10.0
    H0 = 0.5 # 5um
    Hm = 0.03
    # 创建新部件
    myPart = MyModel.Part(
        name="platelet", dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY
    )
    # 创建草图
    mySketch = MyModel.ConstrainedSketch(name="__profile__", sheetSize=200.0)
    # 定义角度（以弧度为单位）
    angle_radians = math.radians(angle_degrees)
    # 定义platelet的尺寸(长度单位是mm)
    L0 = H0 * RHO_P
    Lp = L0
    Hp = H0 - 0.5 * L0 * math.tan(angle_radians)  # 短底厚度
    DELTA_H = 1 / (Hm / H0 + 1)
    Hend = Hm  # matrix等厚
    # 定义阵列的距离
    Interval_X = H0 + Hm
    Interval_Y = Lp / 2 + Hend / 2
    # 定义RVE的尺寸
    L = 2 * (H0 + Hm)  # 这个是厚度
    H = 2 * Interval_Y  # 这个是长度
    # 定义阵列的个数
    number_x = int(L / Interval_X)
    number_y = int(H / Interval_Y)
    # 计算图形的顶点坐标
    x1, y1 = -Hp / 2, -Lp / 2
    x2, y2 = Hp / 2, 0.0 - Lp / 2
    x3, y3 = Hp + Lp / 2 * math.tan(angle_radians) - Hp / 2, Lp / 2 - Lp / 2
    x4, y4 = Hp - Hp / 2, Lp - Lp / 2
    x5, y5 = 0.0 - Hp / 2, Lp - Lp / 2
    x6, y6 = -Lp / 2 * math.tan(angle_radians) - Hp / 2, Lp / 2 - Lp / 2
    # 使用计算得到的坐标点来创建图形
    mySketch.Line(point1=(x1, y1), point2=(x2, y2))
    mySketch.Line(point1=(x2, y2), point2=(x3, y3))
    mySketch.Line(point1=(x3, y3), point2=(x4, y4))
    mySketch.Line(point1=(x4, y4), point2=(x5, y5))
    mySketch.Line(point1=(x5, y5), point2=(x6, y6))
    mySketch.Line(point1=(x6, y6), point2=(x1, y1))
    # 创建 Shell 部件的平面
    myPart.BaseShell(sketch=mySketch)
    # ===================================1.2 建立base=========================================
    s = mdb.models[modelName].ConstrainedSketch(name="__profile__", sheetSize=400.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.rectangle(point1=(0.0, 0.0), point2=(Nx * L, Ny * H))
    p = mdb.models[modelName].Part(
        name="base", dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY
    )
    p = mdb.models[modelName].parts["base"]
    p.BaseShell(sketch=s)
    del mdb.models[modelName].sketches["__profile__"]
    ##==================================1.3 建立阵列后的platelet=======================================
    # 生成platelet的instance
    a = mdb.models[modelName].rootAssembly
    mdb.models[modelName].setValues(noPartsInputFile=ON)
    a.DatumCsysByDefault(CARTESIAN)
    p = mdb.models[modelName].parts["platelet"]
    a.Instance(name="platelet-1", part=p, dependent=ON)
    # 对platelet进行阵列和平移，得到想要的位置
    a.LinearInstancePattern(
        instanceList=("platelet-1",),
        direction1=(1.0, 0.0, 0.0),
        direction2=(0.0, 1.0, 0.0),
        number1=2,
        number2=1,
        spacing1=Interval_X,
        spacing2=Interval_Y,
    )
    a.translate(instanceList=("platelet-1-lin-2-1",), vector=(0.0, -Interval_Y, 0.0))
    # ===================================1.4 (使用布尔运算)阵列得到组合体==============================
    a.LinearInstancePattern(
        instanceList=("platelet-1", "platelet-1-lin-2-1"),
        direction1=(1.0, 0.0, 0.0),
        direction2=(0.0, 1.0, 0.0),
        number1=number_x + 2,
        number2=number_y + 2,
        spacing1=2 * Interval_X,
        spacing2=2 * Interval_Y,
    )
    # 将他们merge起来
    a1 = mdb.models[modelName].rootAssembly
    instances = a1.instances
    dict_listP = instances.values()
    AllInsP = tuple(dict_listP)
    a1.InstanceFromBooleanMerge(
        name="all-platelet", instances=(AllInsP), originalInstances=DELETE, domain=GEOMETRY
    )
    del a1.features["all-platelet-1"]
    # =====================================1.5 根据指定的base修剪all-platelet=========================
    p = mdb.models[modelName].parts["all-platelet"]
    s1 = mdb.models[modelName].ConstrainedSketch(
        name="__profile__", sheetSize=396.95, gridSpacing=9.92
    )
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    s1.rectangle(point1=(0.0, 0.0), point2=(Nx * L, Ny * H))
    s1.rectangle(point1=(-L, -H), point2=(10 * Nx * L, 10 * Ny * H))
    p.Cut(sketch=s1)
    del mdb.models[modelName].sketches["__profile__"]
    # 建立set
    p = mdb.models[modelName].parts["all-platelet"]
    e_platelet_all = p.edges[:]
    f = p.faces
    faces = f[:]
    p.Set(faces=faces, name="P")
    # =====================================1.6 建立matrix,instance=================================
    p = mdb.models[modelName].parts["all-platelet"]
    a1.Instance(name="all-platelet-1", part=p, dependent=ON)
    p = mdb.models[modelName].parts["base"]
    a1.Instance(name="base-1", part=p, dependent=ON)
    # 生成matrix的part和相应的instance
    a1.InstanceFromBooleanCut(
        name="MATRIX",
        instanceToBeCut=mdb.models[modelName].rootAssembly.instances["base-1"],
        cuttingInstances=(a1.instances["all-platelet-1"],),
        originalInstances=DELETE,
    )
    # 建立set
    p = mdb.models[modelName].parts["MATRIX"]
    f = p.faces
    faces = f[:]
    p.Set(faces=faces, name="M")
    a1.regenerate()
    #合并P和M，生成RVE
    a1 = mdb.models[modelName].rootAssembly
    a1.Instance(
        dependent=ON,
        name="all-platelet-1",
        part=mdb.models[modelName].parts["all-platelet"],
    )
    a1.InstanceFromBooleanMerge(name='ALL', instances=(a1.instances['MATRIX-1'], 
        a1.instances['all-platelet-1'], ), keepIntersections=ON, 
        originalInstances=DELETE, domain=GEOMETRY)
    # ------------------------------------------STEP2:划分结构化网格和局部化加密-------------------------------------
    # 建立局部网格划分set
    # 这里仅仅是为了打开sketch界面
    mySketch2 = mdb.models[modelName].ConstrainedSketch(name="__profile__", sheetSize=200.0)
    mySketch2.CircleByCenterPerimeter(center=(-0.02, 0), point1=(-0.03, 0))
    # 使用元组而不是 tuple 函数
    mySketch2.Line(point1=(Hp / 2 + Hm, H - Hend / 2), point2=(0, H - Hend / 2))
    mySketch2.Line(point1=(Hp / 2 + Hm, H - Hend / 2), point2=(Hp / 2 + Hm, H))
    mySketch2.Line(point1=(Hp / 2 + Hm + Hp, H - Hend / 2), point2=(L, H - Hend / 2))
    mySketch2.Line(point1=(Hp / 2 + Hm + Hp, H - Hend / 2), point2=(Hp / 2 + Hm + Hp, H))
    mySketch2.Line(point1=(Hp / 2 + Hm, Hend / 2), point2=(0, Hend / 2))
    mySketch2.Line(point1=(Hp / 2 + Hm, Hend / 2), point2=(Hp / 2 + Hm, 0.0))
    mySketch2.Line(point1=(Hp / 2 + Hm + Hp, Hend / 2), point2=(L, Hend / 2))
    mySketch2.Line(point1=(Hp / 2 + Hm + Hp, Hend / 2), point2=(Hp / 2 + Hm + Hp, 0.0))
    mySketch2.Line(point1=(Hp / 2, Lp / 2), point2=(Hp / 2 + Hm * 2 + Hp, Lp / 2))
    mySketch2.Line(
        point1=(Hp / 2 + Hm * 2 + Hp, Lp / 2), point2=(Hp / 2 + Hm * 2 + Hp, Lp / 2 + Hend)
    )
    mySketch2.Line(
        point1=(Hp / 2 + Hm * 2 + Hp, Lp / 2 + Hend), point2=(Hp / 2, Lp / 2 + Hend)
    )
    mySketch2.Line(point1=(Hp / 2, Lp / 2 + Hend), point2=(Hp / 2, Lp / 2))
    mySketch2.Line(point1=(0.0, Lp / 2 + Hend / 2), point2=(L, Lp / 2 + Hend / 2))
    # 分割面
    #基于“all” part划分面
    partName = 'ALL'
    p = mdb.models[modelName].parts[partName]
    f = p.faces[:]
    p.PartitionFaceBySketch(faces=f, sketch=mySketch2)
    #建立加密mesh Set
    e = p.edges
    edges = e.findAt(((Hp / 2, H - Hend / 4, 0.0),),
            ((Hp / 2 + Hm, H - Hend / 4, 0.0),),
            ((Hp / 2 + Hp + Hm, H - Hend / 4, 0.0),),
            ((Hp / 2 + Hp + 2 * Hm, H - Hend / 4, 0.0),),
            ((Hp / 2, H / 2 + Hend / 4, 0.0),),
            ((0.0, H / 2 + Hend / 4, 0.0),),
            ((0.0, H / 2 - Hend / 4, 0.0),),
            ((L, H / 2 + Hend / 4, 0.0),),
            ((L, H / 2 - Hend / 4, 0.0),),
            ((Hp / 2, H / 2 - Hend / 4, 0.0),),
            ((Hp / 2 + Hm, H / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hm, H / 2 - Hend / 4, 0.0),),
            ((Hp / 2 + Hp + Hm, H / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hp + Hm, H / 2 - Hend / 4, 0.0),),
            ((Hp / 2 + Hp + 2 * Hm, H / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hp + 2 * Hm, H / 2 - Hend / 4, 0.0),),
            ((Hp / 2, Hend / 4, 0.0),),
            ((Hp / 2 + Hm, Hend / 4, 0.0),),
            ((Hp / 2 + Hp + Hm, Hend / 4, 0.0),),
            ((Hp / 2 + Hp + 2 * Hm, Hend / 4, 0.0),),
            ((Hp / 2 + Hm / 2, 0.0, 0.0),),
            ((Hp / 2 + Hm / 2, Hend / 2, 0.0),),
            ((Hp / 2 + Hm / 2, H, 0.0),),
            ((Hp / 2 + Hm / 2, H - Hend / 2, 0.0),),
            ((Hp / 2 + Hm / 2, Hend + Lp / 2, 0.0),),
            ((Hp / 2 + Hm / 2, Lp / 2, 0.0),),
            ((Hp / 2 + Hm / 2, Hend / 2 + Lp / 2, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, Lp / 2, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, Hend + Lp / 2, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, Hend / 2 + Lp / 2, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, H, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, H - Hend / 2, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, 0.0, 0.0),),
            ((Hp / 2 + Hm + Hm / 2 + Hp, Hend / 2, 0.0),),
            ((0.0, H - Hend / 4, 0.0),),
            ((0.0, Hend / 4, 0.0),),
            ((L, H - Hend / 4, 0.0),),
            ((L, Hend / 4, 0.0),),
            ((Hp / 2, H - Hend / 4, 0.0),),
            ((Hp / 2 + 2 * Hm + Hp, H - Hend / 4, 0.0),),
            ((Hp / 2 + Hm, Lp / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hm, Lp / 2 + Hend / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hm + Hp, Lp / 2 + Hend / 4, 0.0),),
            ((Hp / 2 + Hm + Hp, Lp / 2 + Hend / 2 + Hend / 4, 0.0),),
            ((Hp / 2, Hend / 4, 0.0),),
            ((Hp / 2 + 2 * Hm + Hp, Hend / 4, 0.0),),)
    p.Set(edges=edges, name='mesh')
    p = mdb.models[modelName].parts[partName]
    ##全局布种
    p.seedPart(size=0.08, deviationFactor=0.1, minSizeFactor=0.1)
    # 建立加密部分set
    p.seedEdgeByNumber(constraint=FINER, edges=p.sets["mesh"].edges, number=meshNumber)
    f = p.faces[:]
    p.setMeshControls(regions=f, elemShape=QUAD, technique=STRUCTURED)
    p.generateMesh()
    # ==============================================建模完成===========================================
    # ------------------------------------------STEP3:建立horizontal matrix和verticalmatrix SET-------------------------------------
    p = mdb.models[modelName].parts[partName]
    el = p.sets['M'].elements
    tol = 1e-3#这个大小随mesh size变化
    # 这里找horizontal matrix
    x_min, y_min, z_min, x_max, y_max,z_max= Hp/2-tol,Hend/2-tol,0., L-Hp/2+tol,H-Hend/2+tol,0.
    # 框选范围内的元素节点列表
    Horizontal_elements = el.getByBoundingBox(xMin=x_min, yMin=y_min,zMin=z_min,xMax=x_max, yMax=y_max,zMax=z_max)
    p.Set(elements=Horizontal_elements,name='Horizontal_M')
    # 剩余的单元为 allElements - random_elements
    #先找labels
    Horizontal_elements_labels = {elem.label for elem in Horizontal_elements}
    # 根据 label 属性来筛选剩余的元素
    vertical_elements = [elem for elem in el if elem.label not in Horizontal_elements_labels]
    vertical_elementsFormatted = '+'.join(['mdb.models[\'{}\'].parts[\'{}\'].elements[{}:{}]'.format(modelName, 'ALL', elem.label - 1, elem.label) for elem in vertical_elements])
    vertical_elements_set = eval(vertical_elementsFormatted)
    p.Set(elements=vertical_elements_set,name='vertical_M')		
    # ------------------------------------------STEP4:建立LARGE_SCALE_MODEL-------------------------------------
    #NNx = 6
    #NNy = 6
    p.PartFromMesh(name=partName+'-mesh-1', copySets=True)
    p1 = mdb.models[modelName].parts[partName+'-mesh-1']
    a = mdb.models[modelName].rootAssembly
    del a.features[partName+'-1']
    a1 = mdb.models[modelName].rootAssembly
    p = mdb.models[modelName].parts[partName+'-mesh-1']
    a1.Instance(name=partName+'-mesh-1-1', part=p, dependent=ON)
    a1 = mdb.models[modelName].rootAssembly
    a1.LinearInstancePattern(instanceList=(partName+'-mesh-1-1',), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), 
                            number1=NNx, number2=NNy, spacing1=L, spacing2=H)
    a1 = mdb.models[modelName].rootAssembly
    instances = a1.instances
    dict_listP = instances.values()
    AllInsP = tuple(dict_listP)
    a1.InstanceFromBooleanMerge(name='ASS', instances=AllInsP, keepIntersections=ON, originalInstances=DELETE, 
                                mergeNodes=BOUNDARY_ONLY, nodeMergingTolerance=1e-05, domain=BOTH)
    #-----------------------------------预制一个裂纹(长度为一个H厚度)，框选指定单元，然后删除-------------------
    ALLpartName = 'ASS'
    p = mdb.models[modelName].parts[ALLpartName]
    el = p.elements
    tol = 1e-3#这个大小随mesh size变化
    x_min, y_min, x_max, y_max = (NNx-0.5)*L-tol,NNy*H*0.5-Hend-tol, NNx*L+tol,NNy*H*0.5+Hend+tol,
    delete_elements = el.getByBoundingBox(xMin=x_min, yMin=y_min,xMax=x_max, yMax=y_max)
    p.deleteElement(elements=delete_elements)
    #------------------------------------STEP5:材料建立和附截面属性----------------------------
    ALLpartName = 'ASS'
    mdb.models[modelName].Material(name='P')
    mdb.models[modelName].materials['P'].Depvar(n=6)
    mdb.models[modelName].materials['P'].UserMaterial(mechanicalConstants=(
        106000.0, 0.3))
    mdb.models[modelName].Material(name='M')
    mdb.models[modelName].materials['M'].Depvar(n=6)
    mdb.models[modelName].materials['M'].UserMaterial(mechanicalConstants=(modulus_matrix, 
        0.3))
    mdb.models[modelName].Material(name='random')
    mdb.models[modelName].materials['random'].Depvar(n=6)
    mdb.models[modelName].materials['random'].UserMaterial(mechanicalConstants=(modulus_random, 
        0.3))
    mdb.models[modelName].HomogeneousSolidSection(name='P', material='P', 
        thickness=None)
    mdb.models[modelName].HomogeneousSolidSection(name='M', material='M', 
        thickness=None)
    mdb.models[modelName].HomogeneousSolidSection(name='random_M', material='random_horizontal_M', 
        thickness=None) 
    p = mdb.models[modelName].parts[ALLpartName]
    region = p.sets['P']
    p.SectionAssignment(region=region, sectionName='P', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
    #删除多余的M和mesh，避免对后面inp文件的处理带来麻烦
    del mdb.models[modelName].parts[ALLpartName].sets['M']
    del mdb.models[modelName].parts[ALLpartName].sets['mesh']
    #-----------------------------------STEP6:建立step------------------------------------
    mdb.models[modelName].StaticStep(name='Step-1', previous='Initial')
    #-----------------------------基于assembly建立set-------------------------------------
    # 获取总装的根节点
    myModel = mdb.models[modelName]
    myInstance = 'ASS-1'
    rootAssembly = myModel.rootAssembly
    # InstanceName
    partInstanceName = myInstance
    # 获取对应的实例
    partInstance = rootAssembly.instances[partInstanceName]
    # 获取装配体实例中所有节点
    assembly_nodes = partInstance.nodes
    # 遍历所有节点并获取其坐标
    x_coords = [node.coordinates[0] for node in assembly_nodes]
    y_coords = [node.coordinates[1] for node in assembly_nodes]
    # 计算坐标范围
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    tol = 1e-6
    # # 遍历矩形 part 的边上的节点（通过box的框选范围），这里是选取的边，如果只需要点，做相应修改即可
    if kPBC == 1:
        top_load = assembly_nodes.getByBoundingBox(xMin=x_min-tol, yMin=y_max-tol, xMax=x_min+tol, yMax=y_max+tol)
        bottom_1 = assembly_nodes.getByBoundingBox(xMin=x_min-tol, yMin=y_min-tol, xMax=x_min+tol, yMax=y_min+tol)
        bottom_2 = assembly_nodes.getByBoundingBox(xMin=x_max-tol, yMin=y_min-tol, xMax=x_max+tol, yMax=y_min+tol)
        bottoms = bottom_1 + bottom_2
        left_1 = assembly_nodes.getByBoundingBox(xMin=x_min-tol, yMin=y_min-tol, xMax=x_min+tol, yMax=y_min+tol)
        left_2 = assembly_nodes.getByBoundingBox(xMin=x_min-tol, yMin=y_max-tol, xMax=x_min+tol, yMax=y_max+tol)
        lefts = left_1 + left_2
        # 创建矩形四条边上的角点集合(for PBC ONLY)
        top_load_set = rootAssembly.Set(name='LOAD', nodes=top_load)
        bottoms_set = rootAssembly.Set(name='Set-B', nodes=bottoms)
        lefts_set = rootAssembly.Set(name='Set-L', nodes=lefts)
    else:
        top_edge_nodes = assembly_nodes.getByBoundingBox(yMin=y_max-tol, yMax=y_max+tol)
        bottom_edge_nodes = assembly_nodes.getByBoundingBox(yMin=y_min-tol, yMax=y_min+tol)
        left_edge_nodes = assembly_nodes.getByBoundingBox(xMin=x_min-tol, xMax=x_min+tol)
        # 创建矩形四条边上的节点集合
        top_edge_set = rootAssembly.Set(name='LOAD', nodes=top_edge_nodes)
        bottom_edge_set = rootAssembly.Set(name='Set-B', nodes=bottom_edge_nodes)
        left_edge_set = rootAssembly.Set(name='Set-L', nodes=left_edge_nodes)
    a = mdb.models[modelName].rootAssembly
    a.ReferencePoint(point=(0.0, NNy*H, 0.0))
    r1 = a.referencePoints
    index_RP = r1.keys()[-1]
    refPoints1=(r1[index_RP], )
    a.Set(referencePoints=refPoints1, name='RP')
    #: The set 'RP' has been created (1 reference point).
    mdb.models[modelName].Equation(name='Constraint-1', terms=((1.0, 'LOAD', 2), (-1.0, 
        'RP', 2)))
    #----------------------------STEP7:建立边界条件以及外载----------------------------------
    a = mdb.models[modelName].rootAssembly
    region = a.sets['Set-B']
    mdb.models[modelName].DisplacementBC(name='BC-1', createStepName='Initial', 
        region=region, u1=UNSET, u2=SET, ur3=UNSET, amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models[modelName].rootAssembly
    region = a.sets['Set-L']
    mdb.models[modelName].DisplacementBC(name='BC-2', createStepName='Initial', 
        region=region, u1=SET, u2=UNSET, ur3=UNSET, amplitude=UNSET, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models[modelName].rootAssembly
    region = a.sets['RP']
    mdb.models[modelName].DisplacementBC(name='RP', createStepName='Step-1', 
        region=region, u1=UNSET, u2=0.1, ur3=UNSET, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models[modelName].rootAssembly
    a.regenerate()
    #=================================================完成所有的步骤=======================================
    #---------------------------------------------重复建模以及建立相应的job并write-------------------------------
    mdb.models.changeKey(fromName= modelName, toName= NEW_NAME)
    mdb.Job(name=NEW_NAME, model=NEW_NAME, description='', type=ANALYSIS, atTime=None, 
        waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, 
        getMemoryFromAnalysis=True, explicitPrecision=SINGLE, 
        nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, 
        contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', 
        resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=1, 
        activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)
    mdb.jobs[NEW_NAME].writeInput(consistencyChecking=OFF)
    # # 切换工作目录到 Inp 文件夹，如果不存在就创建它
    # new_dir = './PreCrackInp'
    # if not os.path.exists(new_dir):
        # os.makedirs(new_dir)
    # # 切换到指定目录
    # os.chdir(new_dir)
    mdb.jobs[NEW_NAME].writeInput(consistencyChecking=OFF)