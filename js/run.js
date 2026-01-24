#!/usr/bin/env bun
// console.log('loaded', import.meta.url)

import { pathToFileURL } from 'node:url'
import { existsSync, writeFileSync } from 'node:fs'
import { execSync } from 'node:child_process'

export async function complete() {
    const { COMP_LINE, COMP_POINT } = process.env
    const line_prefix = COMP_LINE.slice(0, COMP_POINT)
    const words = line_prefix.split(' ')
    const last_word = words[words.length - 1]
    listFunctions('./Runfile.js', last_word)
}
export async function install() {
    execSync(`
        sudo cp ${import.meta.filename} /usr/local/bin/run.js
        sudo chmod a+x /usr/local/bin/run.js
        echo 'complete -C "run.js .complete" run.js Runfile.js' | tee -a ~/.bashrc
    `)
    console.log('`run.js` installed! restart shell session to use it.')
}

async function listFunctions(filename, prefix) {
    const module = await import(pathToFileURL(filename))
    printFunctions(module, prefix)
}
function printFunctions(module, prefix = '') {
    Object.keys(module)
        .filter(fn => fn.startsWith(prefix))
        .forEach(fn => console.log(fn))
}

function createRunfile(file) {
    const template = `#!/usr/bin/env bun
export function hello() {
    console.log('Hello World!')
}
async function minimain() {
    const module = await import(import.meta.url)
    const [, , name, ...args] = process.argv
    const fn = module[name]
    if (fn) return await fn(...args)
    Object.keys(module).forEach(fn => console.log(fn))
}
if (import.meta.main) minimain()
`
    writeFileSync(file, template, { mode: 0o755 })
    console.log(`${file} created!`)
}

async function runTask(file, name, ...args) {
    const module = await import(pathToFileURL(file))
    const fn = module[name]
    if (!fn) return printFunctions(module)
    return await fn(...args)
}

async function main() {
    let file = './Runfile.js'
    let [, , name, ...args] = process.argv
    if (!name) {
        if (existsSync(file)) return listFunctions(file, '')
        else return createRunfile(file)
    }
    if (name.startsWith('.')) {
        file = import.meta.filename
        name = name.slice(1)
    }
    return await runTask(file, name, ...args)
}

if (import.meta.main) main().catch(console.error)
