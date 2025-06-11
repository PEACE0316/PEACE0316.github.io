#! /user/bin/python
# -*- coding:UTF-8 -*-

#########################################
#########正确可行的版本########
#使用python批量生成inp文件的.bat执行文件#
#########################################

# 导入相关的库
import os
import multiprocessing

#读取计算机的线程
cpus = multiprocessing.cpu_count()
print cpus

#目标路径（在abaqus界面上预先修改文件所在路径）
#dir1 = r'D:\OneDrive - City University of Hong Kong - Student\1 abaqus\TEMP_WORKSTATION'
dir1 = os.getcwd()
#得到路径内所有的文件
names = os.listdir(dir1)
print names

# 建立存储相关文件名的矩阵
inpFile=[]
forFile=[]
otherFile=[]


# 循环得到相应的文件名
for name in names:
	if name.endswith('.inp'):
		inpFile.append(name)
	else:
		if name.endswith('.for'):
			forFile.append(name)
		else:
			otherFile.append(name)
		pass
print(inpFile)
print(forFile)

#创建批处理文件bat
file1 = open('suspend.bat','w')
def FunctionRun(cpu=cpus,com=True,prt=True,sim=True):
	for job in inpFile:
		jobName=job.split('.')[0]
		
		for forfile in forFile:
			forFile1=forfile.split('.')[0]
			if len(inpFile)<len(forFile):
				print(len(inpFile))
				print(len(forFile))
				# JobNameNew = jobName + forFile
				JobNameNew = str(jobName)
			else:
				JobNameNew = str(jobName)
			#JobNameNew = jobName + forfile
			JobNameNew1 = JobNameNew.split('.')[0]
			line = 'cmd/c abaqus suspend job='+JobNameNew1
			file1.write(line)
			file1.write('\n')
	print(JobNameNew)
	file1.write('pause')
	file1.write('\n')
	file1.close()
	print 'Created runFile, I am the princess'
FunctionRun(cpu=1)

















