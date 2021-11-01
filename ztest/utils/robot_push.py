# -*- coding: utf-8 -*-
# @Time    : 2021/9/13 16:56
# @Author  : WuBingTai


from urllib import request
import json

url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxx" #替换自己的key
type = ["#### **<font color=\"warning\">借用测试机</font>**\n", "#### **<font color='info'>归还测试机</font>**\n"]


def push(user, i, phone):
    headers = {'Content-Type': 'application/json'}

    params = {
        "msgtype": "markdown",
        "markdown": {
            "content": type[i] + ">操作人：<font color=\"comment\">" + user + "</font>\n"
                       + ">机型：<font color=\"comment\">" + phone + "</font>"
        }
    }
    req = request.Request(url=url, data=json.dumps(params).encode('utf-8'), headers=headers)
    post_url = request.urlopen(req)
    print(post_url.read().decode('utf-8'))
