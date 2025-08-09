#!/usr/bin/env python3
from run import run_main, sh, sh_out, sh_async, sh_out_async, log

def log_test():
    import time
    log.d("This is an info message.")
    time.sleep(1)
    log.i("This is an info message.")
    time.sleep(1)
    log.w("This is a warning message.")
    time.sleep(1)
    log.e("This is an error message.")

def ssh_test():
    sh('ssh jx')
    
def shell_test():
    p_async_stream = sh_async('sleep 2; uptime') # async, stream
    p_async_pipe = sh_out_async("sleep 1; date") # async, pipe

    print('')

    sh('uname -a') # sync, stream
    version = sh_out('uname -r') # sync, pipe
    print(f'sync pipe, kernel version {version}')

    out, _ = p_async_pipe.communicate()
    print('p_async_pipe', out.strip())
    p_async_stream.wait()

dir_usage = r'''
du -sh . *
'''

def kwargs_test(*args, **kwargs):
    print(args, kwargs)

def list_local_functions():
    for name, sym in globals().items():
        if name.startswith('_'): continue
        if callable(sym) and sym.__module__ == __name__:
            print(name)
def _minimal_main():
    import sys
    if len(sys.argv) == 1: return list_local_functions()
    _, name, *args = sys.argv
    globals()[name](*args)

if __name__ == "__main__":
    _minimal_main()
    # run_main(__file__)
