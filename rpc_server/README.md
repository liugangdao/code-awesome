# rpc调用过程

## 主要包括4个部分
1. 动态代理（主要屏蔽底层细节）
2. 序列化
3. 协议
4. 网络传输

![rpc调用过程](https://github.com/liugangdao/code-awesome/blob/master/rpc_server/doc/rpc.png?raw=true)


## 真正工业级别rpc
该方案还有很多的改进空间，比如socket通讯，可以改进为支持高并发的网络传输方式, 支持protobuf协议等
集群部署还包括
1. 服务发现
2. 路由分组
3. 负载均衡
4. 服务熔断
5. 异常重试
