#!/usr/bin/env python3
import sys
import os
import subprocess
import importlib.util

class Log:
    def __init__(self, name=__name__):
        import logging
        self.log = logging.getLogger(name)
        format = '%(levelname)s %(created)f %(process)d:%(thread)d %(filename)s:%(lineno)d %(message)s'
        logging.basicConfig(format=format, level=logging.DEBUG)
        for idx, char in enumerate('NDIWEF'): logging.addLevelName(idx*10, char)
    def v(self, msg, *args, **kwargs): self.log.debug(msg, stacklevel=2, *args, **kwargs)
    def d(self, msg, *args, **kwargs): self.log.debug(msg, stacklevel=2, *args, **kwargs)
    def i(self, msg, *args, **kwargs): self.log.info(msg, stacklevel=2, *args, **kwargs)
    def w(self, msg, *args, **kwargs): self.log.warning(msg, stacklevel=2, *args, **kwargs)
    def e(self, msg, *args, **kwargs): self.log.error(msg, stacklevel=2, *args, **kwargs)
    def f(self, msg, *args, **kwargs): self.log.critical(msg, stacklevel=2, *args, **kwargs)
log = Log()

def sh(cmds, wait=None, pipe=False):
    stdout = subprocess.PIPE if pipe else None
    process = subprocess.Popen(cmds, shell=True, text=True, stdout=stdout, stderr=stdout)
    if wait == 0: return process
    out, err = process.communicate(timeout=wait)
    if pipe:
        process.stdout = out
        process.stderr = err
    return process

def get_functions(module):
    def is_public_function(obj):
        return \
            callable(obj) and \
            not obj.__name__.startswith('_') and \
            obj.__module__ == module.__name__
    items = vars(module).items()
    return [fn for fn, obj in items if is_public_function(obj)]

def list_functions(filename='Runfile.py'):
    module = load_module(filename)
    for fn in get_functions(module): print(fn)

def load_module(file_path):
    name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(name, file_path)
    return spec.loader.load_module()

def write_text_file(text, file):
    file = os.path.expanduser(file)
    with open(file, "w") as file:
        file.write(text)
def generate_script():
    content = '''#!/usr/bin/env python3
import run
def hello():
    run.log.i('kernel info')
    run.sh("uname -a")
if __name__ == "__main__": run.run_main(__file__)
'''
    file = './Runfile.py'
    write_text_file(content, file)
    os.chmod(file, 0o755)
    print('Runfile.py created!')

def install_bash_completion():
    content = r'''
_run_completion_complete() {
  [[ ! -f ./Runfile.py ]] && return
  local prefix=${COMP_WORDS[$COMP_CWORD]}
  local result=$(compgen -W "$(python3 -m run list_functions)" "$prefix")
  COMPREPLY=($result)
}
_run_completion_install() {
  if [[ -n "${ZSH_VERSION+x}" ]]; then
    ! which compinit >/dev/null && autoload -Uz compinit && compinit
    ! which bashcompinit >/dev/null && autoload -Uz bashcompinit && bashcompinit
  fi
  complete -F _run_completion_complete run Runfile.py
}
_run_completion_install

run() {
  if [[ -z "$@" ]]; then
    if [[ -f ./Runfile.py ]]; then
        python3 ./Runfile.py;
    else
        python3 -m run generate_script;
    fi
  elif [[ "$1" == "-h" ]]; then
    echo "run, the minimalist's task runner - https://github.com/simpzan/run"
  else
    TIMEFORMAT="Task '$1' completed in %3lR"
    time python3 ./Runfile.py "$@"
  fi
}

'''
    completion_file = '~/.run.bash_completion'
    write_text_file(content.lstrip(), completion_file)

    load_script = f'''
# run.py
[[ $PS1 && -f {completion_file} ]] && source {completion_file}
'''
    sh(f'''echo '{load_script}' >> ~/.bashrc''')
    print(f'installed {completion_file}, restart shell session to use it.')

def install():
    site_packages_dir = sys.path[-1]
    current_file_path = os.path.abspath(__file__)
    sh(f'''set -x; cp {current_file_path} {site_packages_dir}''')

    install_bash_completion()
    print('installed `run` command')

def run_task_file(filename, fn, args):
    tasks = load_module(filename)
    if hasattr(tasks, fn):
        getattr(tasks, fn)(*args)
    else: 
        print(f'invalid function: {fn}')
        list_functions(filename)

def run_main(filename):
    if len(sys.argv) < 2:
        if os.path.exists('./Runfile.py'):
            list_functions(filename)
        else:
            generate_script()
        return
    _, fn, *args = sys.argv
    code = run_task_file(filename, fn, args)
    sys.exit(code)

if __name__ == "__main__": run_main(__file__)
