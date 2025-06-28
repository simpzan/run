// console.log('loaded', import.meta.url)

import { pathToFileURL } from 'url';
import { writeFileSync } from 'fs';

const complete_prefix = '${COMP_WORDS[$COMP_CWORD]}'
const _bash_script = `
run_js() {
  if [[ -z "$@" ]]; then
    if [[ -f ./Runfile.js ]]; then
      bun ./Runfile.js
    else
      bun run.js generate_script
    fi
  elif [[ "$1" == "-h" ]]; then
    echo "run, the minimalist's task runner - https://github.com/simpzan/run"
  else
    TIMEFORMAT="Task '$1' completed in %3lR"
    time bun ./Runfile.js "$@"
  fi
}
_run_completion_complete() {
  [[ ! -f ./Runfile.js ]] && return
  local result=$(compgen -W "$(bun ./Runfile.js)" "${complete_prefix}")
  COMPREPLY=($result)
}
complete -F _run_completion_complete run_js Runfile.js
`

export async function install() {
    console.log('Installing...')
    // install bun.js

    // copy run.js
    // write _bash_script
    const bash_file = process.env.HOME + '/.run.js.bash'
    writeFileSync(bash_file, _bash_script.trim(), 'utf8')
    // update ~/.bashrc
}
export async function listFunctions(filename = './Runfile.js') {
    const fileUrl = pathToFileURL(filename)
    const module = await import(fileUrl)
    printFunctions(module)
}
function printFunctions(module) {
    // console.error('No function specified. Available functions:')
    Object.keys(module).forEach(fn => console.log(fn))
}
export async function main(meta) {
    const fileUrl = meta.url
    // console.log(`main(fileUrl: ${fileUrl})`)
    const module = await import(fileUrl)
    const [, , name, ...args] = process.argv
    const fn = module[name]
    if (!fn) return printFunctions(module)
    if (fn === main) return console.error('Cannot call main directly')
    return await fn(...args)
}

if (import.meta.main) main(import.meta).catch(console.error)
