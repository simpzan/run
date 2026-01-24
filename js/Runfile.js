#!/usr/bin/env bun
// console.log('loaded', import.meta.url);

export async function test(...args) {
    console.log('test', args);
    const { $ } = await import("bun");
    const welcome = await $`echo "Hello World!"`.text();
    console.log(welcome); // Hello World!\n
}

export function hello() {
    console.log(`Hello from ${import.meta.filename}`);
}

async function minimain() {
    const module = await import(import.meta.url)
    const [, , name, ...args] = process.argv
    const fn = module[name]
    if (fn) return await fn(...args)
    Object.keys(module).forEach(fn => console.log(fn))
}
if (import.meta.main) minimain()


