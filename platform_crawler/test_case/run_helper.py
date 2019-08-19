def deco(func):
    def wrapper():
        res = func()
        next(res)
        return res
    return wrapper


#@deco
def foo():
    flist = []
    while True:
        food = yield flist, 'sdf'
        flist.append(food)
        print('the flist in function(foo) is %s' % flist)


g = foo()
f1 = next(g)
print(g.send('1111'))
print(g.send('2222'))
print(g.send('3333'))
print(g.send('4444'))
