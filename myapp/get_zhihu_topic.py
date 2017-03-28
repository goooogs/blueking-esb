# -*- coding: utf-8 -*-
"""
Copyright © 2012-2016 Tencent BlueKing. All Rights Reserved. 蓝鲸智云 版权所有
"""
from django import forms

from common.forms import BaseComponentForm
from components.component import Component

from .toolkit import configs
from .toolkit.tools import get_daily_hot_list


class GetZhihuTopic(Component):
    """
    @api {get} /api/c/compapi/myapp/get_zhihu_topic/
    @apiName get_zhihu_topic
    @apiGroup API-MYAPP
    @apiVersion 1.0.0
    @apiDescription 查询知乎热帖
    @apiParam {string} app_code 应用标识，即应用 ID
    @apiParam {string} app_secret 应用私密 key，可以通过 蓝鲸智云开发者中心 -> 点击应用ID -> 基本信息 获取
    @apiParam {string} [bk_token] 当前用户登录态，bk_token与username必须一个有效，bk_token可以通过Cookie获取
    @apiParam {string} [username] 当前用户用户名，白名单中app可使用

    @apiParam {int} record_count 记录个数，即要抓取的记录个数
    @apiParamExample {json} Request-Example:
        {
            "app_code": "esb_test",
            "app_secret": "xxx",
            "bk_token": "xxx",
            "record_count": 100
        }
    @apiSuccessExample {json} Success-Response
        HTTP/1.1 200 OK
        {
            "state": true,
            "message": "第三方接口调用成功",
            "data": {
                "52269362": {
                    "title": "xxx",
                    "answer_id": "xxx",
                    "vote_count": "xxx",
                    "author": "xxx",
                    "bio": "xxx",
                    "summary": "xxx",
                    "href": "xxx",
                },
            },
        }
    """

    # 从 toolkit/configs.py 中获取相关配置
    sys_name = configs.SYSTEM_NAME
    host = configs.host

    class Form(BaseComponentForm):
        # 表单校验，请求该API时必须指定 record_count 参数
        record_count = forms.IntegerField(label=u"记录个数", required=True)

        def clean(self):
            # cleaned_data 对应的是校验后的数据（dict，key是请求API时指定的参数）
            data = self.cleaned_data

            # 以 json 格式返回校验后的数据，方便后续使用
            return {
                'record_count': data['record_count'],
            }

    def handle(self):
        # 获取Form clean处理后的数据
        form_data = self.form_data

        # 设置当前操作者（可以记录到日志系统，本示例中无意义）
        form_data['operator'] = self.current_user.username

        # 组装信息准备发送请求
        host = configs.host.hosts_prod[0]
        path = "explore"
        url = "http://%s:80/%s" % (host, path) # https://hostname/path
        result_json = {}

        # 请求自己封装的逻辑处理接口
        try:
            response = get_daily_hot_list(url=url, record_count=form_data['record_count'])
            result_json = {
                "result": True,
                "data": response,
                "message": u"第三方接口调用成功",
                }
        except Exception as e:
            result_json = {
                "result": False,
                "data": {},
                "message": u"第三方接口调用失败",
                }

        # 设置组件返回结果，payload为组件实际返回结果
        self.response.payload = result_json

