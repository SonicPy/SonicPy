import sys

def foo(*args):
    v,  = args
    return "1-"+"".join(v)

arg = sys.argv[1:]
print(foo(arg))