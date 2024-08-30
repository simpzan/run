#!/usr/bin/env python3
import sys
import os
import subprocess

def run(cmds, wait=5, pipe=False):
    stdout = subprocess.PIPE if pipe else None
    process = subprocess.Popen(cmds, shell=True, text=True, stdout=stdout, stderr=stdout)
    if wait <= 0: return process
    out, err = process.communicate(timeout=wait)
    if pipe:
        process.stdout = out
        process.stderr = err
    return process

def get_functions(module):
    def is_public_function(obj):
        return callable(obj) and not obj.__name__.startswith('_')
    items = vars(module).items()
    return [fn for fn, obj in items if is_public_function(obj)]

def list_functions():
    module = load_runfile()
    for fn in get_functions(module): print(fn)

def load_runfile():
    import importlib.util

    file_path = os.path.join(os.getcwd(), "Runfile.py")

    spec = importlib.util.spec_from_file_location("my_module", file_path)
    module = importlib.util.module_from_spec(spec)
    module = spec.loader.load_module()
    return module

def write_text_file(text, file):
    file = os.path.expanduser(file)
    with open(file, "w") as file:
        file.write(text)
def generate_script():
    content = '''#!/usr/bin/env python3
import sys

def hello(): 
    print(f'hello from {__file__}')

def __main():
    def list_functions():
        for fn, obj in globals().items():
            if callable(obj) and not fn.startswith('_'): print(fn)
    if len(sys.argv) < 2: return list_functions()
    _, name, *args = sys.argv
    code = globals()[name](*args)
    sys.exit(code)
if __name__ == "__main__": __main()
'''
    file = './Runfile.py'
    write_text_file(content, file)
    os.chmod(file, 0o755)
    print('Runfile.py created!')


def list_or_generate_script():
    if os.path.exists('./Runfile.py'):
        list_functions()
    else:
        generate_script()

def install_bash_completion():
    content = r'''
_run_completion_complete() {
  [[ ! -f ./Runfile.py ]] && return
  local prefix=${COMP_WORDS[$COMP_CWORD]}
  local result=$(compgen -W "$(LOCAL=1 run list_functions)" "$prefix")
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
'''
    completion_file = '~/.run.bash_completion'
    write_text_file(content.lstrip(), completion_file)

    load_script = f'''
# run.py
[[ $PS1 && -f {completion_file} ]] && source {completion_file}
'''
    run(f'''echo '{load_script}' >> ~/.bashrc''')
    print(f'installed {completion_file}, restart shell session to use it.')

def install():
    current_file_path = os.path.abspath(__file__)
    run(f'''
TARGET_FILE=/usr/local/bin/run
sudo cp {current_file_path} $TARGET_FILE
sudo chmod 755 $TARGET_FILE
ls -alh $TARGET_FILE
''')

    install_bash_completion()

def run_local_task(fn, args):
    func = globals().get(fn)
    if func is not None:
        func(*args)
        return
def run_runfile_task(fn, args):
    tasks = load_runfile()
    if hasattr(tasks, fn):
        getattr(tasks, fn)(*args)
    else: 
        print(f'invalid function: {fn}')
        list_functions()

def __main():
    # print(sys.argv)
    if len(sys.argv) < 2:
        list_or_generate_script()
        return
    _, fn, *args = sys.argv
    local = os.environ.get("LOCAL", '') == '1'
    if local: run_local_task(fn, args)
    else: run_runfile_task(fn, args)

if __name__ == "__main__": __main()
