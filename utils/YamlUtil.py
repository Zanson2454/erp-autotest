import os
import yaml


class YamlReader:
    # 判断yaml文件是否存在，存在的话赋值给变量self.yamlf，否则引发异常
    def __init__(self, yaml_f):
        if os.path.exists(yaml_f):
            self.yaml_f = yaml_f
        else:
            raise FileNotFoundError("yaml文件不存在")
        self._data = None
        self._data_all = None

    # 判断ymal文件是否为空，若为空则读取文件内容，不为空则直接返回
    def data(self):
        """
        读取单内容的yaml
        :return:
        """
        if not self._data:
            with open(self.yaml_f, "rb") as f:
                self._data = yaml.safe_load(f)
        return self._data

    def data_all(self):
        """
        读取多内容的yaml
        :return:
        """
        if not self._data_all:
            with open(self.yaml_f, "rb") as f:
                # 将生成器转化为列表方便读取，在函数外部读取会报错，with open 自带文件关闭
                self._data_all = list(yaml.safe_load_all(f))
        return self._data_all
