import json

class RpcProtocol:
    """简单RPC协议, 定义请求和响应格式 """
    
    @staticmethod
    def serialize(data):
        """将数据序列化为 JSON 格式"""
        return json.dumps(data).encode('utf-8')
    
    @staticmethod
    def deserialize(data):
        """将数据反序列化为 Python 字典"""
        return json.loads(data.decode('utf-8'))

class RpcRequest:
    """RPC 请求结构"""
    
    def __init__(self, method, params=None):
        self.method = method  # RPC 方法名
        self.params = params if params else []  # 方法参数
    
    def to_dict(self):
        return {
            'method': self.method,
            'params': self.params
        }

class RpcResponse:
    """RPC 响应结构"""
    
    def __init__(self, result=None, error=None):
        self.result = result  # 请求的结果
        self.error = error  # 错误信息
    
    def to_dict(self):
        return {
            'result': self.result,
            'error': self.error
        }