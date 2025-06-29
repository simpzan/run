#!/usr/bin/env bun
// console.log('loaded', import.meta.url)

import { pathToFileURL } from 'url';

export async function complete() {
    const { COMP_LINE, COMP_POINT } = process.env
    const line_prefix = COMP_LINE.slice(0, COMP_POINT)
    const words = line_prefix.split(' ')
    const last_word = words[words.length - 1]
    listFunctions('./Runfile.js', last_word)
}
export async function install() {
    console.log('Installing...')
    const { $ } = await import('bun');
    // install bun.js

    await $`
        sudo cp ${import.meta.filename} /usr/local/bin/run.js
        sudo chmod a+x /usr/local/bin/run.js
        echo 'complete -C "run.js .complete" run.js' | tee -a ~/.bashrc
    `
}
export async function listFunctions(filename, prefix) {
    const fileUrl = pathToFileURL(filename)
    const module = await import(fileUrl)
    printFunctions(module, prefix)
}
function printFunctions(module, prefix = '') {
    // console.error('No function specified. Available functions:')
    Object.keys(module)
        .filter(fn => fn.startsWith(prefix))
        .forEach(fn => console.log(fn))
}
export async function main(meta) {
    let file = './Runfile.js'
    let [, , name, ...args] = process.argv
    if (!name) return listFunctions(file, '')
    if (name.startsWith('.')) {
        file = import.meta.file
        name = name.slice(1)
    }
    const module = await import(pathToFileURL(file))
    const fn = module[name]
    if (!fn) return printFunctions(module)
    if (fn === main) return console.error('Cannot call main directly')
    return await fn(...args)
}

if (import.meta.main) main(import.meta).catch(console.error)
