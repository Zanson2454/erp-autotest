import requests

def send_dingtalk_msg(webhook: str, content: str):
    """
    发送钉钉文本消息
    :param webhook: 钉钉机器人 webhook 地址
    :param content: 消息内容
    """
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    resp = requests.post(webhook, json=data, headers=headers)
    resp.raise_for_status()
    return resp.json() 