---
layout: post
title: ABAQUS 如何实现动画与曲线视图同步并输出到PPT中
categories: Simulation
description: 在后处理过程中，为了更加清晰和生动的表达模型的变形情况，可以考虑将动画与变形曲线同步显示，然后输出到PPT中向老板展示
keywords: 动画输出，视图同步
---

## 1. 分析完成，打开 Visualization 界面，以下图为例
![image](https://user-images.githubusercontent.com/67852601/219600416-b43138bc-97f3-4f74-acb5-0e430e5840fa.png)
## 2. 新建一个视图（viewpoint），并绘制需要的曲线![image](https://user-images.githubusercontent.com/67852601/219601112-7237263c-0e5d-438a-a5b3-d8cd03182058.png)
## 3. 关联这两个视图（linked viewpoint）
![image](https://user-images.githubusercontent.com/67852601/219601269-cb910b21-41df-4de7-94c2-2714b5dc542a.png)
## 4. 关联上指定的视图 （Link viewpoints），并指定排列方式 ![image](https://user-images.githubusercontent.com/67852601/219602697-44357d28-6d35-4106-b187-7002c2679d16.png)

![image](https://user-images.githubusercontent.com/67852601/219601602-9d662596-3b69-443c-8dc5-c26cd83e390b.png)
![image](https://user-images.githubusercontent.com/67852601/219602875-f7bdc035-0717-4ce4-888b-659a4cc54f6d.png)

## 5. 打开动画（Animate：Time history）
![image](https://user-images.githubusercontent.com/67852601/219603362-962a388d-c531-4891-8770-7155dcb9f98e.png)

### 打开动画设置选项，根据需要进行设置
![image](https://user-images.githubusercontent.com/67852601/219604110-68f66675-da92-4802-bf58-6efac1a18cc4.png)

## 6. 保存动画

![image](https://user-images.githubusercontent.com/67852601/219609644-f19ae4fd-5cda-4b5c-9ba9-ae71e4aab4c4.png)

## 7. 完成
在PPT中导入该文件即可
