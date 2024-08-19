---
layout: post
title: How to batch processing the inp files by Python?
categories: Simulation
description: 基于python的批处理
keywords: python, inp
---
### 实现这个目的需要系统学习python吗？学习这个技能有什么必要性吗？
当我们使用abaqus进行参数化分析时，手动修改某一参数，比如施加的载荷、载荷的施加角度、结构的厚度等，如果案例只有一两个，手动调参，然后提交任务，都是非常简单且不怎么费时费力的事，然而，当我们想要改变几十甚至上百次参数才能得到我们想要的结果时，会不会因为这些重复且无意义的机械劳动而陷入沉思，我这和机器有什么区别？哈哈哈，如果有这种念头，说明你来对地方了，也恭喜你发现了你作为人的主观能动性，那么标题上的问题也就有了答案！话不多说，让我们开始吧！
### 以一个简单的程序为例，讲讲我们实现批处理的核心思想和实现手段

假设已知inp文件如下：
---
此处省略

---
'''
###! /usr/bin/python
### -*- coding: UTF-8 -*-

#########################################
######### 正确可行的版本 ########
### 使用python批量生成inp文件的.bat执行文件 #
#########################################

### 导入相关的库
import os
import multiprocessing

### 读取计算机的线程
cpus = multiprocessing.cpu_count()
print(cpus)

### 目标路径
dir1 = os.getcwd()
### 得到路径内所有的文件
names = os.listdir(dir1)
print(names)

### 建立存储相关文件名的矩阵
inpFile = []
forFile = []
otherFile = []

### 循环得到相应的文件名
for name in names:
    if name.endswith('.inp'):
        inpFile.append(name)
    elif name.endswith('.for'):
        forFile.append(name)
    else:
        otherFile.append(name)

print(inpFile)
print(forFile)

### 创建批处理文件bat
with open('run.bat', 'w') as file1:
    def FunctionRun(cpu, job):
        jobName = job.split('.')[0]
        JobNameNew = str(jobName)
        line = 'cmd /c abaqus job=' + JobNameNew + ' input=' + job + ' cpus=' + str(cpu)
        file1.write(line)
        file1.write('\n')
        print("Job added to bat file:", JobNameNew)

    for job in inpFile:
        FunctionRun(cpu=1, job=job)

    file1.write('pause\n')
    print('Created runFile, I am the princess')

### 输出批处理文件的内容以进行验证
with open('run.bat', 'r') as file1:
    print(file1.read())
'''
