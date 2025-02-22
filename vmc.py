#!/usr/bin/env python3.12
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

def gpu(vm=None, devices=None):
    if not vm:
        sh('lspci | grep -E "acc|Display"')
        return
    cmd = f'virt-xml {vm} --remove-device --host-dev all\n'
    suffix = [f'--host-dev {dev}' for dev in devices.split(',')]
    cmd += f'virt-xml {vm} --add-device ' + ' '.join(suffix)
    print(cmd)
    sh(cmd)

def ls():
    vms = _get_vm_list()
    for name in vms:
        running = vms[name]
        pci = _get_pci_devices(name)
        print(f'{name:<{40}}\t {running}\t {pci}')

def _get_pci_devices(vm):
    cmd = f'virsh dumpxml "{vm}"'
    texts = sh_out(cmd).strip()
    out = _parse_pci_addresses(texts)
    return out

def _get_ip_of_vm(vm):
    cmd = f'virsh domifaddr {vm}'
    line = sh_out(cmd).strip().split('\n')[-1]
    ip_full = line.split(' ')[-1]
    ip = ip_full.split('/')[0]
    print(ip)
    return ip

def _wait_host(ip):
    sh(f'until nc -vzw 2 "{ip}" 22; do sleep 2; done')

def ssh(vm, command=None):
    ip = _get_ip_of_vm(vm)
    # if not ip:
    #     print('ip not found, try again later')
    #     import time
    #     time.sleep(1) 
    #     ip = _get_ip_of_vm(vm)
    if not ip: return -1
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
