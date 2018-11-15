# AwesomeCRM
这是一个学员管理的CRM项目，下载时请忽略***photo***目录
## 项目环境
Django 2.1.1

python 3.7.0

sqlite3

## 项目介绍
### 自定义了一套增删改查系统
**主要使用了ModelForm技术**

这套增删改查系统，只需要给出models里面相关表对应类，就能够在前端自动生成增删改查的表单，其中的查询可以自定义。

可以通过input框搜索；

也可以通过select框筛选，其中筛选的条件还可以自定义；

还定义了一个Action功能，可以对数据进行批量操作，具体的操作内容，可以使用钩子函数自定制，非常方便

### 实现了一套通用的权限管理方案
在权限管理方便，自定义了一套通用的权限管理方案，通过配合Django的权限管理，实现了对每一条url进行拦截

通过对要拦截的url字典配置，可以精确的拦截到url，以及请求方式(GET还是POST)，以及可以指定必须带有的参数，甚至指定所带的参数的值必须是什么。

当然，拦截的这么精确就一定会有弊端，这个弊端就是url字典的配置太过麻烦，于是在每条url的后面加了一个钩子函数，可以根据具体情况进行自定义拦截

## 项目展示

__销售页面__
销售可以查看客户库，客户库可以进行一系列查询操作，可以在代码中自定义
![customerInfo](https://github.com/Traeric/AwesomeCRM/blob/master/photo/customerInfo.png)

添加客户，这是根据Django的ModelForm自动生成的
![customer add](https://github.com/Traeric/AwesomeCRM/blob/master/photo/addCustomer.png)

客户报名
![studnt emrollment](https://github.com/Traeric/AwesomeCRM/blob/master/photo/enrollement.png)

客户填写报名表
![emrollment1](https://github.com/Traeric/AwesomeCRM/blob/master/photo/enrollment1.png)
![enrollment2](https://github.com/Traeric/AwesomeCRM/blob/master/photo/enrollment2.png)

__学生页面__
提交作业
![submit homework](https://github.com/Traeric/AwesomeCRM/blob/master/photo/submit_homework.png)

__老师页面__
管理班级
![manage class](https://github.com/Traeric/AwesomeCRM/blob/master/photo/class_manage.png)

查看上课记录
![course record](https://github.com/Traeric/AwesomeCRM/blob/master/photo/course_record.png)

检查作业
![check homework](https://github.com/Traeric/AwesomeCRM/blob/master/photo/homework.png)

这里拎了几个比较重要的页面，还有很多页面不做赘述


