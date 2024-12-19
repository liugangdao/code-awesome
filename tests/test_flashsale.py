from queue import Queue
import threading
from flash_sale_func.flashsale import FlashSaleSystem

# 测试模拟秒杀请求
def simulate_seckill(seckill_system, user_id, result_queue):
    """模拟一个用户参与秒杀"""
    success = seckill_system.attempt_purchase(user_id)
    result_queue.put((user_id, success))

def run_seckill_test():
    """运行秒杀测试，模拟多个用户秒杀"""
    seckill_system = FlashSaleSystem(product_id="12345", stock=5)
    result_queue = Queue()

    # 模拟10个用户同时进行秒杀请求
    threads = []
    for i in range(10):
        user_id = f"user{i}"
        thread = threading.Thread(target=simulate_seckill, args=(seckill_system, user_id, result_queue))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # 输出结果
    while not result_queue.empty():
        user_id, success = result_queue.get()
        status = "成功" if success else "失败"
        print(f"用户 {user_id} 秒杀 {status}，当前库存: {seckill_system.get_stock()}")

if __name__ == "__main__":
    run_seckill_test()