import asyncio
from collections.abc import Iterable
from typing import Callable, Any, Optional, Coroutine, List


async def async_main(task: Callable, maxNum: int, doneNum: int, args: list):
    '''并发任务控制'''
    async def main_task(sem):
        async with sem:
            await task(*args)
    sem = asyncio.Semaphore(maxNum)
    task_list = []
    for _ in range(doneNum):
        task_io = asyncio.create_task(main_task(sem))
        task_list.append(task_io)
    await asyncio.gather(*task_list)


class runFoeverByTime:
    '''设置总事件循环超时，一旦超时，所有未完成的任务都会停止'''

    def __init__(self, timeout) -> None:
        self.time = timeout
        self.loop = asyncio.get_event_loop()
        self()
        ...

    def __call__(self):
        async def wait():
            await asyncio.sleep(self.time)
            self.loop.stop()
        self.loop.create_task(wait())
        self.loop.run_forever()
        pass


class runFoeverUntilStop:
    '''完成所有的任务之后立刻停止，(同步阻塞代码)'''

    def __init__(self, loop=asyncio.get_event_loop()):
        self.loop = loop
        self()

    def __call__(self, *args: Any, **kwds: Any) -> Any:

        self.tasks_list = list(asyncio.all_tasks(self.loop))
        self.length = len(self.tasks_list)
        if self.length <= 0:
            return

        def callback(x):
            self.length -= 1
            if self.length <= 0:
                self.loop.stop()
        for task in self.tasks_list:
            task.add_done_callback(callback)
        self.loop.run_forever()


async def reRunWhenTimeout(asyncFunction, timeout: float):
    '''超时后重新运行asyncFunction'''
    success = 0
    while success == 0:
        try:
            await asyncio.wait_for(asyncFunction(), timeout=timeout)
            success = 1
        except:
            success = 0


class dataGetListener:
    '''数据调用监听器,callback中请不要再次调用相关属性'''
    nihao = 100
    __instance: Optional['dataGetListener'] = None
    static_data = None

    def __new__(cls, *args, **kwargs):
        dataGetListener.__instance = super().__new__(cls)
        return dataGetListener.__instance

    def __init__(self, data):
        self.data = data

    @staticmethod
    async def Callback(__name):
        await asyncio.sleep(5)
        if dataGetListener.__instance != None:
            print('the data is ', dataGetListener.static_data)

    def __getattribute__(self, __name: str) -> Any:
        print(__name)
        data = super(dataGetListener, self).__getattribute__(__name)
        if __name == 'data':
            loop = asyncio.get_event_loop()
            loop.create_task(dataGetListener.Callback(__name))
            dataGetListener.static_data = data
        return data


def taskSequence(coros: List[Coroutine[Any, Any, Any]], loop=asyncio.get_event_loop()) -> List[Any]:
    '''为任务添加顺序控制,按照传入的coros的顺序添加入任务队列'''
    result = []

    async def f():
        for coro in coros:
            result.append(await coro)
    loop.create_task(f())
    return result


class deepSearchSync:
    '''tree接受树,branch接受属性,以字符串表示,val代表节点的值,branch属性值必须是一个可迭代对象'''

    def __init__(self, tree, branch: str, val: str, callback: Optional[Callable] = None):
        if not hasattr(tree, branch):
            raise IndexError('the branch must instance branch')
        self.tree = tree
        self.branch = branch
        self.val = val
        self.callback = callback
        self.__get()

    def __get(self):
        # 默认是广搜
        '''0是广度优先,1是深度优先'''
        que = [self.tree]
        while len(que) > 0:
            node = que.pop(0)
            try:
                val = getattr(node, self.val)
                branches = getattr(node, self.branch)
                if self.callback:
                    self.callback(val)
            except:
                print("deepSearch : you don't set branch or val!!!")
                return
            if isinstance(branches, Iterable):
                for node in branches:
                    if type(node) != type(self.tree):
                        raise IndexError('the branch must instance branch')
                    que.append(node)


class deepSearchASync:
    '''tree接受树,branch接受属性,以字符串表示,val代表节点的值,branch属性值必须是一个可迭代对象,回调若是传入了同步函数,就会以同步的方式调用'''

    def __init__(self, tree, branch: str, val: str, callback: Optional[Callable] = None, loop=asyncio.get_event_loop()):
        if not hasattr(tree, branch):
            raise IndexError('the branch must instance branch')
        self.tree = tree
        self.branch = branch
        self.val = val
        self.callback = callback
        self.loop = loop
        self.__get()

    def __get(self):
        # 默认是广搜
        que = [self.tree]
        while len(que) > 0:
            node = que.pop(0)
            try:
                val = getattr(node, self.val)
                branches = getattr(node, self.branch)
                if self.callback:
                    if asyncio.coroutines.iscoroutinefunction(self.callback):
                        self.loop.create_task(self.callback(val))
                    elif callable(self.callback):
                        self.callback(val)
            except:
                print("deepSearch : you don't set branch or val!!!")
                return
            if isinstance(branches, Iterable):
                for node in branches:
                    if type(node) != type(self.tree):
                        raise IndexError('the branch must instance branch')
                    que.append(node)
