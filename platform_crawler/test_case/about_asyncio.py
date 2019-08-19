import asyncio

async def work1():
    print('running work1')
    await asyncio.sleep(2)
    await consm(1)
    return 'work1 res'

async def work2():
    print('running work2')
    await asyncio.sleep(3)
    await consm(2)
    return 'work2 res'

async def consm(num):
    print(f'in consm cor get {num}')


# ****** sec entrance
def run_pro_and_cons():     # 生产者和消费者模式
    task = asyncio.gather(work1(), work2())
    return event_loop.run_until_complete(task)


# ****** sec entrance
def run_sec():
    task = [
        asyncio.ensure_future(work1()),
        asyncio.ensure_future(work2())
    ]
    return event_loop.run_until_complete(asyncio.wait(task))        # param 接受coroutine 对象或future对象
    # asyncio.wait(task) 将task打包成future对象       # 返回(set(done:r1, 22), set(pending))


# ============ aiohttp -- client =================
import aiohttp
async def fetch_page():
    url = 'http://144.34.194.228/sef'
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=3) as resp:
                assert 'response status not 200: %s' % (resp.status == 200)
                res = await resp.text()
                print(res)
        except Exception as e:
            import traceback
            traceback.print_exc()


# ****** sec entrance
def run_fetch_page():
    event_loop.run_until_complete(fetch_page())

# 信号量，控制并发访问
NUMBERS = range(6)
URL = 'http://httpbin.org/get?a={}'
sema = asyncio.Semaphore(3)


async def fetch_async(a):
    async with aiohttp.request('GET', URL.format(a)) as r:
        data = await r.json()
    return data['args']['a']


async def print_result(a):
    async with sema:
        r = await fetch_async(a)
        print(f'fetch({a}) = {r}')


# ****** sec entrance
def run_semaphore_async():
    f = asyncio.wait([print_result(num) for num in NUMBERS])
    event_loop.run_until_complete(f)


# =============   Event 事件处理
def set_event(event):
    print('setting event in callback')
    event.set()


async def test(name, event):
    print('{} waiting for event'.format(name))
    await event.wait()
    print('{} triggered'.format(name))


# ****** sec entrance
async def main(loop):
    import functools
    event = asyncio.Event()
    print('event start state: {}'.format(event.is_set()))
    loop.call_later(0.1, functools.partial(set_event, event))       # 延迟0.1秒回调set_event函数
    await asyncio.wait([test('e1', event), test('e2', event)])
    print('event end state: {}'.format(event.is_set()))


# 优先级队列  -----   Queue   -----
import random
NUMBERS_QUEUE = random.sample(range(100), 7)


async def collect_result(a):
    async with sema:
        return await fetch_async(a)


async def produce(queue):
    for num in NUMBERS_QUEUE:
        print(f'producing {num}')
        item = (num, num)
        await queue.put(item)


async def consume(queue):
    while 1:
        item = await queue.get()
        num = item[0]
        rs = await collect_result(num)
        print(f'consuming {rs}...')
        queue.task_done()


async def queue_run():
    queue = asyncio.PriorityQueue()
    consumer = asyncio.ensure_future(consume(queue))
    await produce(queue)
    await queue.join()
    consumer.cancel()


# ****** sec entrance
def quque_main():
    event_loop.run_until_complete(queue_run())




if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    quque_main()
    event_loop.close()

