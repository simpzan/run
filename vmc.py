#!/usr/bin/env python3
import sys
import os
import subprocess
import time
import xml.etree.ElementTree as ET

def sh(cmds, wait=None, pipe=False):
    stdout = subprocess.PIPE if pipe else None
    process = subprocess.Popen(cmds, shell=True, text=True, stdout=stdout, stderr=stdout)
    if wait == 0: return process
    out, err = process.communicate(timeout=wait)
    if pipe:
        process.stdout = out
        process.stderr = err
    return process
def sh_out(cmds):
    return sh(cmds, pipe=True).stdout

def _get_vm_list():
    texts = sh_out(f'virsh list --all')
    lines = texts.strip().split('\n')[2:]
    vms = {}
    for line in lines:
        info = line.split(' ')
        _, name, state, *_ = [e for e in info if len(e) > 0]
        vms[name] = state == 'running'
    return vms

def vm_info(vm):
    vms = _get_vm_list()
    running = vms[vm]
    pci = _get_pci_devices(vm)
    cpu_core = _get_cpu_count(vm)
    memory = _get_memory(vm)
    ip = _get_ip_of_vm(vm)
    hdd = _get_hdd(vm)
    print(f'''
Name: {vm}
Running: {running}
CPU cores: {cpu_core:<{3}}
System Memory: {memory:.1f}
PCI: {pci}
IP: {ip}
HDD: {hdd}
'''.strip())
    sh(f'qemu-img info {hdd} | grep -E "backing file:|virtual size|disk size"')

def info(vm=None):
    if vm: return vm_info(vm)
    print('\n---------------- CPU ----------------')
    cpu()
    print('\n---------------- MEM ----------------')
    mem()
    print('\n---------------- GPU ----------------')
    gpu()
    print('')

def mem(vm=None, size=None):
    if not vm:
        sh('free -h')
        return
    size = int(size) * 1024 * 1024
    print(f"<memory unit='KiB'>{size}</memory><currentMemory unit='KiB'>{size}</currentMemory>")
    input("press Enter to start edit xml file:")
    sh(f'virsh edit {vm}')

def cpu(vm=None, count=None):
    if not vm:
        sh('lscpu | grep -E "^CPU\(s\):|NUMA node"')
        return
    sh(f'virt-xml {vm}  --edit --vcpus {count}')

def gpu(vm=None, devices=None):
    if not vm:
        sh('lspci | grep -E "acc|Display"')
        return
    cmd = f'virt-xml {vm} --remove-device --host-dev all\n'
    suffix = [f'--host-dev {dev}' for dev in devices.split(',')]
    cmd += f'virt-xml {vm} --add-device ' + ' '.join(suffix)
    print(cmd)
    sh(cmd)

def _get_cpu_count(vm):
    out = sh_out(f'virsh vcpucount {vm} | grep current | grep config')
    out = out.strip().split(' ')[-1]
    return int(out)

def _get_memory(vm):
    cmd = f'virsh dumpxml "{vm}"'
    xml_string = sh_out(cmd).strip()
    el = ET.fromstring(xml_string).find('.//currentMemory')
    out = int(el.text) / 1024 / 1024
    return out

def ls():
    vms = _get_vm_list()
    name_len_max = max([len(name) for name in vms])
    print(f'{"NAME":<{name_len_max}}\t STATE\tCPU  MEM   PCI')
    for name in vms:
        running = vms[name]
        pci = _get_pci_devices(name)
        cpu = _get_cpu_count(name)
        mem = _get_memory(name)
        print(f'{name:<{name_len_max}}\t {running}\t{cpu:<{3}}  {mem:.1f}  {pci}')

def _get_pci_devices(vm):
    texts = sh_out(f'virsh dumpxml "{vm}"').strip()
    out = []
    for element in ET.fromstring(texts).findall(".//devices/hostdev/source/address"):
        keys = ['domain', 'bus', 'slot', 'function']
        domain, bus, device, function = [element.attrib[key][2:] for key in keys]
        bdf = f'{domain}:{bus}:{device}.{function}'
        out.append(bdf)
    return out

def _get_ip_of_vm(vm):
    cmd = f'virsh domifaddr {vm}'
    line = sh_out(cmd).strip().split('\n')[-1]
    if not 'ipv4' in line: return
    ip_full = line.split(' ')[-1]
    ip = ip_full.split('/')[0]
    return ip

def _wait_host(ip):
    sh(f'until nc -vzw 2 "{ip}" 22; do sleep 2; done')

def ssh(vm, command=None):
    vms = _get_vm_list()
    if not vms[vm]: return print(f'Error: vm {vm} not running')
    while True:
        ip = _get_ip_of_vm(vm)
        if ip: break
        print('ip not found, try again later')
        time.sleep(2)
    _wait_host(ip)
    cmd = f'sshpass -p amd1234 ssh -o StrictHostKeyChecking=no root@{ip}'
    if command: cmd += f' -t "{command}"'
    sh(cmd)

def run(vm, cmd=None):
    vms = _get_vm_list()
    if not vms[vm]: start(vm)
    ssh(vm, cmd)

def _change_name_to_ip(filepath):
    if ':' not in filepath: return filepath
    vm, file = filepath.split(':')
    ip = _get_ip_of_vm(vm)
    return f'root@{ip}:{file}'

def scp(src, dst):
    src = _change_name_to_ip(src)
    dst = _change_name_to_ip(dst)
    cmd = f'sshpass -p amd1234 scp -r {src} {dst}'
    sh(cmd)

def install():
    cmd = f'apt install guestfs-tools sshpass'

def _get_hdd(vm):
    out = sh_out(f'virsh domblklist {vm} | grep -E "vda|hda"')
    hdd = out.strip().split(' ')[-1]
    return hdd

def _fork_one_vm(base, base_hdd, vm):
    new_hdd = f'{os.path.dirname(base_hdd)}/{vm}.qcow2'
    cmd = f'''qemu-img create -f qcow2 -F qcow2 -b {base_hdd} "{new_hdd}" &&
        virt-clone --original "{base}" --name "{vm}" --file "{new_hdd}" --preserve-data &&
        virt-sysprep -d {vm} --operation machine-id'''
    sh(cmd)
def fork(base, *vms):
    base_hdd = _get_hdd(base)
    backing_file = sh_out(f'qemu-img info {base_hdd} | grep -E "backing file:"').strip()
    if backing_file:
        print(f'Warn: the disk of the vm is derived disk!\n{base}: {base_hdd}\n{backing_file}')
    for vm in vms: _fork_one_vm(base, base_hdd, vm)

def rm(*vms, **kwargs):
    options = '--remove-all-storage' if '--rs' in kwargs else ''
    for vm in vms: sh(f'virsh undefine {options} {vm}')

def start(*vms):
    for vm in vms: sh(f'virsh start {vm}')

def stop(*vms, **kwargs):
    vms_info = _get_vm_list()
    if '--all' in kwargs: vms = vms_info.keys()
    for vm in vms:
        if vms_info[vm]: sh(f'virsh destroy {vm}')

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
def _main():
    if len(sys.argv) < 2:
        for sym, obj in globals().items():
            if not sym.startswith('_') and callable(obj): print(sym)
        return
    _, name, *args = sys.argv
    sym = globals()[name]
    if callable(sym):
        args, kwargs = _parse_kwargs(args)
        sym(*args, **kwargs)
if __name__ == "__main__": _main()
