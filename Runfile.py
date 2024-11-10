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

if __name__ == "__main__": run_main(__file__)
