#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib.util

class _Log:
    def __init__(self, name=__name__):
        import logging
        self.log = logging.getLogger(name)
        format = '%(levelname)s %(created)f %(process)d:%(thread)d %(filename)s:%(lineno)d %(message)s'
        logging.basicConfig(format=format, level=logging.DEBUG)
        for idx, char in enumerate('NDIWEF'): logging.addLevelName(idx*10, char)
    def v(self, msg='', *args, **kwargs): self.log.debug(msg, stacklevel=2, *args, **kwargs)
    def d(self, msg='', *args, **kwargs): self.log.debug(msg, stacklevel=2, *args, **kwargs)
    def i(self, msg='', *args, **kwargs): self.log.info(msg, stacklevel=2, *args, **kwargs)
    def w(self, msg='', *args, **kwargs): self.log.warning(msg, stacklevel=2, *args, **kwargs)
    def e(self, msg='', *args, **kwargs): self.log.error(msg, stacklevel=2, *args, **kwargs)
    def f(self, msg='', *args, **kwargs): self.log.critical(msg, stacklevel=2, *args, **kwargs)
log = _Log()

def sh(cmds, wait=None, pipe=False):
    stdout = subprocess.PIPE if pipe else None
    process = subprocess.Popen(cmds, shell=True, universal_newlines=True, stdout=stdout, stderr=stdout)
    if wait == 0: return process
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

def _get_functions(module):
    def is_public(name, obj):
        if name.startswith('_'): return False
        if isinstance(obj, str): return True
        return callable(obj) and obj.__module__ == module.__name__
    items = vars(module).items()
    return [fn for fn, obj in items if is_public(fn, obj)]

def list_functions(filename='Runfile.py', prefix=''):
    module = _load_module(filename)
    for fn in _get_functions(module):
        if fn.startswith(prefix): print(fn)

def _load_module(file_path):
    file_path = os.path.abspath(file_path)
    main = sys.modules['__main__']
    if os.path.abspath(main.__file__) == file_path: return main

    name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(name, file_path)
    return spec.loader.load_module()

def _write_text_file(text, file, mode='w'):
    file = os.path.expanduser(file)
    with open(file, mode) as file:
        file.write(text)

_template_Runfile_py = '''
#!/usr/bin/env python3
from run import sh, log, run_main
def hello():
    log.i('kernel info')
    sh("uname -a")
if __name__ == "__main__": run_main(__file__)
'''
def generate_script():
    file = 'Runfile.py'
    _write_text_file(_template_Runfile_py.lstrip(), file)
    os.chmod(file, 0o755)
    print(f'{file} created!')

def install():
    current_file_path = os.path.abspath(__file__)
    run_file = '/usr/local/bin/run.py'
    sh(f'''
sudo cp {current_file_path} {run_file};
sudo chmod a+x {run_file};
echo 'complete -C "{run_file} complete" run.py Runfile.py' | tee -a ~/.bashrc;
echo '`run.py` installed! restart shell session to use it.'
    ''')

def complete(*_):
    comp_line = os.getenv('COMP_LINE', '')
    comp_point = int(os.getenv('COMP_POINT', len(comp_line)))
    line_prefix = comp_line[:comp_point]
    words = line_prefix.split(' ')
    last_word = words[-1] if words else ''

    list_functions('./Runfile.py', last_word)

def _run_task_file(filename, fn, args):
    tasks = _load_module(filename)
    if not hasattr(tasks, fn):
        print(f'invalid function: {fn}')
        list_functions(filename)
        return -1
    sym = getattr(tasks, fn)
    if callable(sym):
        args, kwargs = _parse_kwargs(args)
        return sym(*args, **kwargs)
    return sh(sym).returncode

def _parse_kwargs(all_args):
    kwargs = {}
    args = []
    for arg in all_args:
        if not arg.startswith('--'): args.append(arg)
        elif not '=' in arg: kwargs[arg] = ''
        else:
            key, value = arg.split('=')
            kwargs[key] = value
    return args, kwargs

def run_main(filename):
    if len(sys.argv) < 2: return list_functions(filename)
    _, fn, *args = sys.argv
    code = _run_task_file(filename, fn, args)
    sys.exit(code)

if __name__ == "__main__": run_main(__file__)
