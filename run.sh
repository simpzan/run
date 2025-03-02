#!/bin/bash

_run_init_gen() { cat > $1 << 'EOF'
#!/bin/bash
set -euo pipefail
help() { echo "run, the minimalist's task runner - https://github.com/simpzan/run"; }

main_() {
  if [[ -z "$@" ]]; then
    compgen -A function | grep -v "_$"
  elif declare -F "$1" >/dev/null; then
    "$@"
  else
    echo "Error: unknown function '$1'" >&2
  fi
}
main_ $@
EOF
}
_run_init() {
  printf 'create Runfile? (Y/n)'; read answer
  [[ "$answer" == "n" ]] && return
  _run_init_gen ./Runfile && chmod a+x $_
  echo "created Runfile."
}
_run_tasks() {
  echo "Tasks in Runfile:"
  ./Runfile | cat -n
}
run() {
  if [[ -z "$@" ]]; then
    if [[ -f ./Runfile ]]; then _run_tasks; else _run_init; fi
  elif [[ "$1" == "-h" ]]; then
    echo "run, the minimalist's task runner - https://github.com/simpzan/run"
  else
    TIMEFORMAT="Task '$1' completed in %3lR"
    time ./Runfile "$@"
  fi
}

_run_completion_complete() {
  [[ ! -f ./Runfile ]] && return
  local prefix=${COMP_WORDS[$COMP_CWORD]}
  local result=$(compgen -W "$(./Runfile)" "$prefix")
  COMPREPLY=($result)
}
_run_completion_install() {
  if [[ -n "${ZSH_VERSION+x}" ]]; then
    ! which compinit >/dev/null && autoload -Uz compinit && compinit
    ! which bashcompinit >/dev/null && autoload -Uz bashcompinit && bashcompinit
  fi
  complete -F _run_completion_complete run Runfile
}
_run_file_append_if() {
  local rc=$1 cmd=$2
  grep -q "$cmd" $rc 2>/dev/null || echo "$cmd" >> $rc
}
_run_install() {
  local selfPath=$0
  local file=.run.sh
  cp $selfPath ~/$file
  local cmd="[[ -f ~/$file ]] && source ~/$file"
  _run_file_append_if ~/.bashrc "$cmd"
  _run_file_append_if ~/.zshrc "$cmd"
  echo "run command installed, restart shell session to use it."
}
if [[ "$0" == "$BASH_SOURCE" ]]; then _run_install; else _run_completion_install; fi
