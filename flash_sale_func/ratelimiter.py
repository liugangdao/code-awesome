import time
import redis

class RateLimiter:

    def __init__(self,redis_client, product_id, bucket_capacity=1000,leak_rate=50):
        """
        :param redis_client: Redis 客户端实例
        :param product_id: 产品 ID，作为漏桶的唯一标识
        :param bucket_capacity: 漏桶容量（最大请求数）
        :param leak_rate: 漏桶泄漏速率（单位：qps，表示每秒从桶中泄漏的请求数）
        """
        self.redis_client = redis_client
        self.product_id = product_id
        self.bucket_capacity = bucket_capacity
        self.leak_rate = leak_rate
    
    def _rate_limit(self):
        """使用 Redis 实现漏桶算法限流"""
        current_time = int(time.time())  # 获取当前时间戳（秒）
        bucket_key = f"leaky_bucket:{self.product_id}"

        # 将当前时间戳（请求时间）作为数据项放入 Redis 列表
        self.redis_client.lpush(bucket_key, current_time)

        # 设置漏桶最大容量：限制列表中的最大元素数
        self.redis_client.ltrim(bucket_key, 0, self.bucket_capacity - 1)

        # 获取漏桶中的所有时间戳
        timestamp_list = self.redis_client.lrange(bucket_key, 0, self.bucket_capacity - 1)

        # 判断桶中的请求数是否超出速率限制
        if len(timestamp_list) > self.bucket_capacity:
            # 如果漏桶已满，则丢弃请求
            return False
        
        expiry_time = current_time - 1

        # 如果当前请求在漏桶中且没有超出容量和速率限制，允许通过
        while timestamp_list and int(timestamp_list[-1]) <= expiry_time:
            self.redis_client.rpop(bucket_key)  # 删除过期的请求

        if len(timestamp_list) <= self.leak_rate:
            return True
        
        return False