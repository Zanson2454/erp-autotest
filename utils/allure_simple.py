#!/usr/bin/env python3
# coding=utf-8
"""
Allure简易辅助工具
提供简单的方法来生成美观的Allure报告，减少代码重复
"""

import json
import allure
from contextlib import contextmanager
from typing import Dict, Any, Optional

class AllureSimple:
    """
    极简的Allure辅助类，提供最基本的功能封装
    
    主要功能：
    1. 简化JSON附件添加
    2. 简化文本附件添加
    3. 提供更简洁的步骤上下文管理器
    
    使用示例:
        from utils.allure_simple import a
        
        # 添加JSON附件
        a.json(data, "请求数据")
        
        # 添加文本附件
        a.text("一些文本信息", "文本数据")
        
        # 使用步骤上下文管理器
        with a.step("执行某个步骤"):
            # 步骤内的代码
            result = do_something()
            # 添加步骤结果作为附件
            a.json(result, "步骤结果")
    """
    
    @staticmethod
    def json(data: Dict[str, Any], name: str = "数据") -> None:
        """
        添加JSON数据作为附件
        
        Args:
            data: 要添加的JSON数据(字典对象)
            name: 附件名称，默认为"数据"
        
        说明:
            自动将字典转换为格式化的JSON字符串，并设置正确的附件类型
        """
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name=name,
            attachment_type=allure.attachment_type.JSON
        )
    
    @staticmethod
    def text(text: str, name: str = "文本") -> None:
        """
        添加文本数据作为附件
        
        Args:
            text: 要添加的文本数据
            name: 附件名称，默认为"文本"
        
        说明:
            将文本内容直接添加为附件，并设置正确的附件类型
        """
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    @contextmanager
    def step(name: str):
        """
        步骤上下文管理器，简化步骤的创建
        
        Args:
            name: 步骤名称
        
        使用示例:
            with a.step("步骤1: 准备数据"):
                data = prepare_data()
        
        说明:
            使用Python的上下文管理器(with语句)实现步骤的自动开始和结束
        """
        with allure.step(name):
            yield
    
    @staticmethod
    def add_description(description: str) -> None:
        """
        动态添加测试描述
        
        Args:
            description: Markdown格式的描述文本
        
        说明:
            在测试运行时动态添加或修改测试描述
        """
        allure.dynamic.description(description)
    
    @staticmethod
    def add_title(title: str) -> None:
        """
        动态添加测试标题
        
        Args:
            title: 测试标题
        
        说明:
            在测试运行时动态添加或修改测试标题
        """
        allure.dynamic.title(title)

# 创建一个全局实例方便导入
a = AllureSimple() 