import queue
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Optional, Dict, List, Union

日志 = logging.getLogger("任务执行器")
日志.propagate = False  # 阻止传播到父 logger

# 添加独立的处理器（如果需要输出到控制台）
if not 日志.handlers:
    日志.addHandler(logging.StreamHandler())

class 高级函数队列执行器:
    """高级函数队列执行器 - 支持多函数、多任务排队、可选线程执行方式
        def 示例函数1(参数1, 参数2=None):
        import time
        print(f"[示例函数1] 开始执行: 参数1={参数1}, 参数2={参数2}")
        time.sleep(2)
        print("[示例函数1] 执行完成")
        return f"结果1: {参数1}, {参数2}"


    def 示例函数2(名称, 数量):
        import time
        print(f"[示例函数2] 开始执行: 名称={名称}, 数量={数量}")
        time.sleep(1)
        print("[示例函数2] 执行完成")
        return f"结果2: {名称} x {数量}"


    def 回调函数(结果, 异常):
        if 异常:
            print(f"[回调] 任务失败: {异常}")
        else:
            print(f"[回调] 任务成功: {结果}")


    try:
        # 创建执行器
        执行器 = 高级函数队列执行器(最大工作线程=2, 队列大小=10, 默认异步=True)

        print("\n=== 测试1: 提交多个异步任务 ===")
        future1 = 执行器.提交任务(
            示例函数1,
            "任务1",
            参数2="测试",
            任务ID="task_1",
            回调函数=回调函数
        )

        future2 = 执行器.提交任务(
            示例函数2,
            "苹果",
            数量=5,
            任务ID="task_2",
            回调函数=回调函数
        )

        future3 = 执行器.提交任务(
            示例函数1,
            "任务3",
            参数2="另一个测试",
            任务ID="task_3"
        )
        for i in range(20):
            future3 = 执行器.提交任务(
                示例函数1,
                "任务3",
                参数2=f"另一个测试{i}",
                任务ID="task_3"
            )

        print("队列状态:", 执行器.获取队列状态())

        print("\n=== 测试2: 提交同步任务 ===")
        # 同步执行（会阻塞当前线程）
        同步结果 = 执行器.提交任务(
            示例函数2,
            "同步任务",
            数量=3,
            异步=False
        )
        print(f"同步任务结果: {同步结果}")
        for i in range(20):
            future3 = 执行器.提交任务(
                示例函数1,
                "任务3",
                参数2=f"另一个测试{i}",
                任务ID="task_3"
            )

        print("\n=== 测试3: 等待特定任务完成 ===")
        执行器.等待任务完成(任务ID="task_1")
        result1 = 执行器.获取任务结果("task_1")
        print(f"任务1结果: {result1}")

        print("\n=== 测试4: 等待所有任务完成 ===")
        执行器.等待任务完成()
        print("所有任务已完成")

        print("\n=== 任务统计 ===")
        print(执行器.获取任务统计())

        # 获取所有任务结果
        for 任务ID in ["task_1", "task_2", "task_3"]:
            result = 执行器.获取任务结果(任务ID)
            print(f"{任务ID}: {result}")

    except Exception as e:
        print(f"程序出错: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # 关闭执行器
        print("\n关闭执行器...")
        执行器.关闭()
        print("程序结束")
    """

    def __init__(self, 最大工作线程=3, 队列大小=100, 默认异步=True):
        """
        初始化高级函数队列执行器

        参数:
            最大工作线程: 线程池最大工作线程数
            队列大小: 任务队列最大大小
            默认异步: 是否默认以异步方式执行任务
        """
        self.线程池 = ThreadPoolExecutor(max_workers=最大工作线程)
        self.任务队列 = queue.Queue(maxsize=队列大小)
        self.最大工作线程 = 最大工作线程
        self.队列大小 = 队列大小
        self.默认异步 = 默认异步
        self.锁 = threading.RLock()
        self.运行状态 = True
        self.活跃任务数 = 0
        self.已完成任务数 = 0
        self.任务结果 = {}  # 存储任务结果
        self.任务回调 = {}  # 存储任务回调函数

        # 启动任务处理线程
        self.处理线程 = threading.Thread(target=self._任务处理循环, daemon=True)
        self.处理线程.start()

        日志.info(f"高级函数队列执行器已启动，最大线程数: {最大工作线程}, 队列大小: {队列大小}")

    def 提交任务(
            self,
            函数: Callable,
            *args,
            异步: Optional[bool] = None,
            任务ID: Optional[str] = None,
            回调函数: Optional[Callable] = None,
            **kwargs
    ) -> Optional[Future]:
        """
        提交函数任务到队列

        参数:
            函数: 要执行的函数
            *args: 函数的位置参数
            异步: 是否异步执行（None: 使用默认设置, True: 线程异步, False: 阻塞执行）
            任务ID: 任务标识符（用于获取结果）
            回调函数: 任务完成后的回调函数
            **kwargs: 函数的关键字参数

        返回:
            Future对象（如果异步执行）或 函数执行结果（如果同步执行）
        """
        if not self.运行状态:
            日志.warning("执行器已关闭，无法提交新任务")
            return None

        # 确定执行方式
        执行异步 = self.默认异步 if 异步 is None else 异步

        # 生成任务ID
        if 任务ID is None:
            任务ID = f"任务_{int(time.time() * 1000)}_{self.已完成任务数 + 1}"

        # 创建任务信息
        任务信息 = {
            '函数': 函数,
            'args': args,
            'kwargs': kwargs,
            '异步': 执行异步,
            '任务ID': 任务ID,
            '回调函数': 回调函数,
            '提交时间': time.time()
        }

        try:
            if 执行异步:
                # 异步执行：将任务放入队列
                with self.锁:
                    self.任务队列.put_nowait(任务信息)
                    self.活跃任务数 += 1
                    #日志.debug(f"任务已提交到队列: {任务ID}")

                    # 创建Future对象用于跟踪任务
                    future = Future()
                    self.任务结果[任务ID] = {'future': future, '状态': '排队中'}
                    return future
            else:
                # 同步执行：直接在当前线程执行
                #日志.debug(f"同步执行任务: {任务ID}")
                try:
                    结果 = 函数(*args, **kwargs)
                    #日志.debug(f"同步任务完成: {任务ID}")

                    # 如果提供了回调函数
                    if 回调函数:
                        try:
                            回调函数(结果)
                        except Exception as e:
                            日志.error(f"回调函数执行失败: {str(e)}")

                    return 结果

                except Exception as e:
                    日志.error(f"同步任务执行失败 {任务ID}: {str(e)}")
                    raise

        except queue.Full:
            日志.warning(f"任务队列已满，无法提交任务: {任务ID}")
            return None
        except Exception as e:
            日志.error(f"提交任务失败: {str(e)}")
            return None

    def _任务处理循环(self):
        """后台任务处理循环"""
        while self.运行状态 or not self.任务队列.empty() or self.活跃任务数 > 0:
            try:
                # 从队列获取任务（阻塞，但会超时以检查运行状态）
                try:
                    任务信息 = self.任务队列.get(timeout=0.1)
                except queue.Empty:
                    continue

                任务ID = 任务信息['任务ID']
                函数 = 任务信息['函数']
                args = 任务信息['args']
                kwargs = 任务信息['kwargs']
                回调函数 = 任务信息['回调函数']

                #日志.debug(f"开始处理任务: {任务ID}")

                # 提交到线程池执行
                future = self.线程池.submit(self._执行任务, 任务信息)

                # 存储future用于后续跟踪
                with self.锁:
                    if 任务ID in self.任务结果:
                        self.任务结果[任务ID]['future'] = future
                        self.任务结果[任务ID]['状态'] = '执行中'
                    else:
                        self.任务结果[任务ID] = {
                            'future': future,
                            '状态': '执行中',
                            '提交时间': 任务信息['提交时间']
                        }

                # 添加完成回调
                future.add_done_callback(lambda f: self._任务完成回调(f, 任务ID, 回调函数))

            except Exception as e:
                日志.error(f"任务处理循环出错: {str(e)}")

    def _执行任务(self, 任务信息):
        """执行具体任务"""
        任务ID = 任务信息['任务ID']
        函数 = 任务信息['函数']
        args = 任务信息['args']
        kwargs = 任务信息['kwargs']

        try:
            #日志.debug(f"执行任务 {任务ID}: {函数.__name__}")
            #开始时间 = time.time()

            # 执行函数
            结果 = 函数(*args, **kwargs)

            #耗时 = time.time() - 开始时间
            #任务完成日志.debug(f"任务完成 {任务ID}, 耗时: {耗时:.2f}s")

            return 结果

        except Exception as e:
            日志.error(f"任务执行失败 {任务ID}: {str(e)}")
            raise

    def _任务完成回调(self, future, 任务ID, 回调函数=None):
        """任务完成回调处理"""
        with self.锁:
            self.活跃任务数 -= 1
            self.已完成任务数 += 1
            self.任务队列.task_done()

        # 更新任务状态
        with self.锁:
            if 任务ID in self.任务结果:
                self.任务结果[任务ID]['状态'] = '已完成'
                self.任务结果[任务ID]['完成时间'] = time.time()

                # 存储结果
                try:
                    self.任务结果[任务ID]['结果'] = future.result()
                except Exception as e:
                    self.任务结果[任务ID]['异常'] = str(e)

        # 执行用户提供的回调函数
        if 回调函数 and not future.cancelled():
            try:
                if future.exception():
                    回调函数(None, future.exception())
                else:
                    回调函数(future.result(), None)
            except Exception as e:
                日志.error(f"用户回调函数执行失败: {str(e)}")

        #日志.debug(f"任务回调处理完成: {任务ID}")

    def 等待任务完成(self, 任务ID: Optional[str] = None, 超时: Optional[float] = None):
        """
        等待特定任务或所有任务完成

        参数:
            任务ID: 要等待的任务ID，None表示等待所有任务
            超时: 超时时间（秒）
        """
        if 任务ID:
            # 等待特定任务
            if 任务ID in self.任务结果:
                future = self.任务结果[任务ID].get('future')
                if future:
                    try:
                        future.result(timeout=超时)
                    except Exception as e:
                        日志.warning(f"等待任务 {任务ID} 时出错: {str(e)}")
        else:
            # 等待所有任务
            self.任务队列.join()

            # 等待所有活跃任务完成
            开始时间 = time.time()
            while self.活跃任务数 > 0:
                if 超时 and (time.time() - 开始时间) > 超时:
                    日志.warning("等待所有任务完成超时")
                    break
                time.sleep(0.1)

    def 获取任务结果(self, 任务ID: str, 超时: Optional[float] = None):
        """
        获取特定任务的结果

        参数:
            任务ID: 任务标识符
            超时: 等待结果的最大时间

        返回:
            任务结果 或 None（如果失败）
        """
        if 任务ID not in self.任务结果:
            日志.warning(f"任务ID不存在: {任务ID}")
            return None

        任务数据 = self.任务结果[任务ID]
        future = 任务数据.get('future')

        if future:
            try:
                return future.result(timeout=超时)
            except Exception as e:
                日志.error(f"获取任务结果失败 {任务ID}: {str(e)}")
                return None
        elif '结果' in 任务数据:
            return 任务数据['结果']
        else:
            return None

    def 获取队列状态(self) -> Dict:
        """获取队列状态信息"""
        with self.锁:
            return {
                "队列大小": self.队列大小,
                "当前队列任务数": self.任务队列.qsize(),
                "队列是否为空": self.任务队列.empty(),
                "队列是否已满": self.任务队列.full(),
                "最大工作线程": self.最大工作线程,
                "活跃任务数": self.活跃任务数,
                "已完成任务数": self.已完成任务数,
                "运行状态": self.运行状态,
                "默认异步执行": self.默认异步
            }

    def 设置默认异步(self, 异步: bool):
        """设置默认执行方式"""
        self.默认异步 = 异步
        日志.info(f"默认执行方式已设置为: {'异步' if 异步 else '同步'}")

    def 清空队列(self):
        """清空任务队列"""
        with self.锁:
            while not self.任务队列.empty():
                try:
                    self.任务队列.get_nowait()
                    self.任务队列.task_done()
                except queue.Empty:
                    break
            self.活跃任务数 = 0
            日志.info("任务队列已清空")

    def 关闭(self, 等待完成: bool = True):
        """
        关闭执行器

        参数:
            等待完成: 是否等待所有任务完成后再关闭
        """
        日志.info("正在关闭执行器...")
        self.运行状态 = False

        if 等待完成:
            日志.info("等待所有任务完成...")
            self.等待任务完成(超时=30)

        # 清空队列（不再接受新任务）
        self.清空队列()

        # 关闭线程池
        self.线程池.shutdown(wait=等待完成)

        日志.info("执行器已关闭")

    def 获取任务统计(self) -> Dict:
        """获取任务统计信息"""
        with self.锁:
            return {
                "总提交任务数": self.已完成任务数 + self.活跃任务数,
                "已完成任务数": self.已完成任务数,
                "活跃任务数": self.活跃任务数,
                "队列等待任务数": self.任务队列.qsize(),
                "任务结果数量": len(self.任务结果)
            }

