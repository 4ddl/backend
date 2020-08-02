import os


# 从操作系统中读取环境变量
def env(key, val=None):
    return os.environ.get(key) or val
