from rpc_server.protocol import RpcProtocol,RpcRequest,RpcResponse
import socket
import threading

class RpcServer:
    """RPC 服务器类, 提供服务并处理请求"""

    def __init__(self,host="localhost", port=50051,buffer_size=1024) -> None:
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.services = {}

    def register_service(self,name,service):
        """注册服务"""
        self.services[name] = service
    
    def handle_request(self, client_socket):
        """处理来自客户端的请求"""
        try:
            # 接受请求数据
            data = client_socket.recv(self.buffer_size)
            request_data = RpcProtocol.deserialize(data)
            method_name = request_data['method']
            params = request_data['params']

            if method_name in self.services:
                service = self.services[method_name]
                result = service(*params)
                response = RpcResponse(result=result)
            else:
                response = RpcResponse(error=f"Method {method_name} not found")

            # 序列化响应并发送给客户端
            response_data = RpcProtocol.serialize(response.to_dict())
            client_socket.send(response_data)
        
        except Exception as e:
            # 发生错误时的处理
            response = RpcResponse(error=str(e))
            response_data = RpcProtocol.serialize(response.to_dict())
            client_socket.send(response_data)
        
        finally:
            client_socket.close()
    
    def start(self):
        """启动服务器并监听请求"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host,self.port))
            server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")
            while True:
                client_socket,_=server_socket.accept()
                threading.Thread(target=self.handle_request,args=(client_socket,)).start()
    

class RpcClient:
    """RPC 客户端类，支持通过网络调用服务"""

    def __init__(self, host="localhost", port=50051,buffer_size=1024):
        self.host = host
        self.port = port
        self.buffer_size= buffer_size
    
    def call(self, method, *params):
        """调用远程方法"""

        try:
            # 构造rpc请求
            request = RpcRequest(method, params)
            request_data = RpcProtocol.serialize(request.to_dict())
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.host, self.port))
                client_socket.send(request_data)
                
                # 接收响应
                response_data = client_socket.recv(1024)
                response_dict = RpcProtocol.deserialize(response_data)
                
                if response_dict['error']:
                    return f"Error: {response_dict['error']}"
                return response_dict['result']
        except Exception as e:
            return f"Error: {str(e)}"