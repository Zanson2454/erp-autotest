import os
import glob
import yaml
import requests
import sys
from pathlib import Path
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
logger.info(f"project_root: {project_root}")

from utils.yaml_util import YamlUtil


md_api_path_yaml = Path(project_root, 'testdata', 'erp_fin','fin_api_path.yaml')
md_api_path = YamlUtil.read_yaml(md_api_path_yaml).get('apis', {})


# 直接在代码中配置 headers
HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://t-erp-console-test.app.terminus.io/team/22/app/SCM_SLS/folder/SCM_SLS%24e57ef38a-ba6f-4f41-a91b-b112b0ecfab4',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Trantor2-App': 'SCM_SLS',
    'Trantor2-Team': '22',
    'Trantor2-TrantorTeamDTO': '22',
    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    "Cookie":"t_iam_test=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbklkIjoiMjAyNTA3MjExMDQ3MTU1NTc4NzZmNjkyYmY0N2M0NzU2YjEyMDExYzk3OWFkZmZhOCIsImV4cGlyZSI6MjU5MjAwLCJwYXRoIjoiLyIsImRvbWFpbiI6InRlcm1pbnVzLmlvIiwiaHR0cE9ubHkiOnRydWUsInNlY3VyZSI6ZmFsc2UsImlzcyI6ImlhbSgyLjUuMjUuMDUzMC4wLVNOQVBTSE9UKSIsInN1YiI6ImlhbSB1c2VyIiwiZXhwIjoxNzUzMzU0OTgxLCJuYmYiOjE3NTMwOTU3ODEsImlhdCI6MTc1MzA5NTc4MSwianRpIjoiZGEyZmU0Y2I2NTAwNDVjMTgzOWYyZjM1NGNiMjlkYWQifQ.-GmiHxTPEHySZwVAnc8tIcjhagyT5jfA7N8UbJyr2M4"
}

# 提取所有服务
servers = []
for k,v in md_api_path.items():
    path = v.get("path")
    if not path:
        continue
    service_key = path.split('/')[-1]
    if service_key:
        servers.append(service_key)
logger.info(f"共提取到 {len(servers)} 个服务")


# 遍历所有服务，查询是否被引用
def check_service(server):
    url = f'https://t-erp-console-test.app.terminus.io/api/trantor/console/resource-node/usage-tree?direction=Backward&key={server}'
    try:
        resp = requests.get(url, headers=HEADERS, cookies=None, timeout=10)
        if resp.status_code != 200:
            logger.error(f"服务 {server} 查询失败，状态码: {resp.status_code}")
            return None
        data = resp.json()
        logger.info(f"服务 {server} 查询结果: {data}")
        if not data.get('data', {}).get('modules'):
            logger.info(f"未被引用: {server}")
            return server
    except Exception as e:
        logger.error(f"服务 {server} 查询异常: {e}")
    return None

unreferenced_services = set()
with ThreadPoolExecutor(max_workers=10) as executor:  # 10可根据带宽和接口限制调整
    future_to_server = {executor.submit(check_service, server): server for server in servers}
    for future in as_completed(future_to_server):
        result = future.result()
        if result:
            unreferenced_services.add(result)

unreferenced_services =set(unreferenced_services)
logger.info(f"未被引用的服务key 有: { len(unreferenced_services)} 个")

output_path = Path(__file__).parent / "unreferenced_services_fin_api_path.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for key in sorted(unreferenced_services):
        f.write(key + "\n")
logger.info(f"未被引用的服务key已写入: {output_path}") 


