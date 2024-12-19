import redis
import threading
import time
from collections import defaultdict
from queue import Queue
from flash_sale_func.ratelimiter import RateLimiter

class FlashSaleSystem:
    def __init__(self, product_id, stock, redis_host='localhost', redis_port=6379):
        """初始化秒杀系统，指定商品ID和库存数"""
        self.product_id = product_id
        self.stock = stock
        self.orders = set()  # 用于存储已经购买过商品的用户ID，防止重复下单
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0)
        self.rateLimiter = RateLimiter(self.redis_client,product_id)
        self.lock = threading.Lock()  # 线程锁，保证并发安全
        self.bucket_capacity = 10  # 漏桶容量
        self.leak_rate = 1  # 每秒漏出1个请求

    def _acquire_lock(self):
        """尝试获取分布式锁"""
        lock_key = f"flashsale_lock:{self.product_id}"
        lock = self.redis_client.setnx(lock_key, 1)  # 使用 SETNX 命令设置锁
        if lock:
            self.redis_client.expire(lock_key, 10)  # 锁10秒
        return lock

    def _release_lock(self):
        """释放分布式锁"""
        lock_key = f"flashsale_lock:{self.product_id}"
        self.redis_client.delete(lock_key)

    def attempt_purchase(self, user_id):
        """尝试购买商品"""
        # 限流检查
        if not self.rateLimiter._rate_limit():
            return False  # 如果超过了限流次数，秒杀失败

        # 获取分布式锁，确保同一时刻只有一个请求能修改库存
        if not self._acquire_lock():
            return False  # 获取锁失败，秒杀失败

        try:
            # 核心秒杀逻辑
            with self.lock:  # 内存锁，保证同一时刻只有一个线程修改库存
                if user_id in self.orders:
                    return False  # 用户已经购买过商品
                if self.stock > 0:
                    self.stock -= 1  # 库存减少
                    self.orders.add(user_id)  # 记录用户已购买
                    return True  # 成功购买
                return False  # 库存不足
        finally:
            self._release_lock()  # 释放分布式锁


    def get_stock(self):
        """获取当前库存"""
        return self.stock
