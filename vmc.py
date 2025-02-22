#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from run import sh, sh_out, log, run_main

def _parse_pci_addresses(xml_string):
    try:
        root = ET.fromstring(xml_string)
        addresses = []
        for element in root.findall(".//devices/hostdev/source/address"):
            keys = ['domain', 'bus', 'slot', 'function']
            domain, bus, device, function = [element.attrib[key][2:] for key in keys]
            bdf = f'{domain}:{bus}:{device}.{function}'
            addresses.append(bdf)
        return addresses
    except Exception as e: # Catch other potential errors
        print(f"An unexpected error occurred: {e}")
        return

def _get_vm_list():
    texts = sh_out(f'virsh list --all')
    lines = texts.strip().split('\n')[2:]
    vms = {}
    for line in lines:
        info = line.split(' ')
        _, name, state, *_ = [e for e in info if len(e) > 0]
        vms[name] = state == 'running'
    return vms

def info():
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
    cmd = f'virsh dumpxml "{vm}"'
    texts = sh_out(cmd).strip()
    out = _parse_pci_addresses(texts)
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
        import time
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

def fork(base, vm):
    base_hdd = _get_hdd(base)
    import os.path
    new_hdd = os.path.dirname(base_hdd) + vm + '.qcow2'
    cmd = f'''qemu-img create -f qcow2 -F qcow2 -b {base_hdd} "{new_hdd}" &&
        virt-clone --original "{base}" --name "{vm}" --file "{new_hdd}" --preserve-data &&
        virt-sysprep -d {vm} --operation machine-id'''
    sh(cmd)

def rm(vm):
    sh(f'virsh undefine {vm}')

def start(vm):
    sh(f'virsh start {vm}')

def stop(vm):
    if vm != '--all':
        sh(f'virsh destroy {vm}')
        return
    vms = _get_vm_list()
    for vm in vms:
        if vms[vm]: sh(f'virsh destroy {vm}')

if __name__ == "__main__": run_main(__file__)
