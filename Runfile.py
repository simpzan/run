#!/usr/bin/env python3
import sys
import subprocess

import logging
format = '%(levelno)s %(created)f %(process)d:%(thread)d %(filename)s:%(lineno)d %(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)
class log:
    @staticmethod
    def v(msg, *args, **kwargs): logging.debug(msg, *args, **kwargs)
    @staticmethod
    def d(msg, *args, **kwargs): logging.debug(msg, *args, **kwargs)
    @staticmethod
    def i(msg, *args, **kwargs): logging.info(msg, *args, **kwargs)
    @staticmethod
    def w(msg, *args, **kwargs): logging.warning(msg, *args, **kwargs)
    @staticmethod
    def e(msg, *args, **kwargs): logging.error(msg, *args, **kwargs)
    @staticmethod
    def f(msg, *args, **kwargs): logging.critical(msg, *args, **kwargs)

def log_test():
    import time
    time.sleep(1)
    log.i("This is an info message.")
    time.sleep(1)
    log.w("This is a warning message.")
    time.sleep(1)
    log.e("This is an error message.")

# sync or not, pipe or get result
def sh(cmds, wait=5, pipe=False):
    stdout = subprocess.PIPE if pipe else None
    process = subprocess.Popen(cmds, shell=True, text=True, stdout=stdout, stderr=stdout)
    if wait <= 0: return process
    out, err = process.communicate(timeout=wait)
    if pipe:
        process.stdout = out
        process.stderr = err
    return process
def sh_out(cmds):
    return sh(cmds, pipe=True).stdout
def sh_async(cmds):
    return sh(cmds, wait=0)
def sh_out_async(cmds):
    return sh(cmds, wait=0, pipe=True)

def shell(func):
    def wrapper_shell(*args, **kwargs):
        return sh(func.__doc__)
    return wrapper_shell

@shell
def kernel_info(): r'''
uname -a
'''

def sh_test():        
    sh('''
uname -r
pwd
       ''')
    
def test():
    p_async_stream = sh_async('sleep 2; uptime') # async, stream
    p_async_pipe = sh_out_async("sleep 1; date") # async, pipe

    print('')

    sh('uname -a') # sync, stream
    version = sh_out('uname -r') # sync, pipe
    print(f'sync pipe, kernel version {version}')

    out, _ = p_async_pipe.communicate()
    print('p_async_pipe', out.strip())
    p_async_stream.wait()

def __main():
    def list_functions():
        for fn, obj in globals().items():
            if callable(obj) and not fn.startswith('_'): print(fn)
    if len(sys.argv) < 2: return list_functions()
    _, name, *args = sys.argv
    code = globals()[name](*args)
    sys.exit(code)
if __name__ == "__main__": __main()
