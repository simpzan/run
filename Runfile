#!/bin/bash
set -euo pipefail
git.config() {
  git config --global alias.co checkout
  git config --global alias.br branch
  git config --global alias.cm commit
  git config --global alias.ca 'commit --amend'
  git config --global alias.st status
  git config --global core.editor "vim"
}
node.install() {
  curl -fsSL https://fnm.vercel.app/install | bash
  ~/.fnm/fnm install v16.13.2
}
node.httpserver.install() {
  npm install -g http-server
}
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
