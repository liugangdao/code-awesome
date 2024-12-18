import threading

import sys
import os

# 获取当前工作目录
current_dir = os.getcwd()

# 获取父目录并添加到 sys.path
# parent_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
print(sys.path)
from rpc_server.rpc import RpcServer,RpcClient
class CalculatorService:
    """示例计算器服务"""

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

# 启动服务器并注册服务
def start_server():
    server = RpcServer(host='localhost', port=50051)
    calculator_service = CalculatorService()
    
    # 注册服务
    server.register_service('add', calculator_service.add)
    server.register_service('subtract', calculator_service.subtract)
    
    # 启动服务器
    server.start()

# 客户端调用服务
def start_client():
    client = RpcClient(host='localhost', port=50051)
    
    # 调用服务
    result = client.call('add', 10, 20)
    print(f"Result of add: {result}")
    
    result = client.call('subtract', 20, 10)
    print(f"Result of subtract: {result}")

if __name__ == "__main__":
    
    # 启动服务器
    threading.Thread(target=start_server, daemon=True).start()
    
    # 启动客户端
    start_client()
