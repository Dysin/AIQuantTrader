'''
@Desc:   获取本机配置信息工具
@Author: Dysin
@Date:   2025/10/6
'''

import socket
import platform
import uuid
try:
    import psutil
except ImportError:
    psutil = None
try:
    import requests
except ImportError:
    requests = None
from tabulate import tabulate

def get_basic_system_info():
    uname = platform.uname()
    return {
        "hostname": socket.gethostname(),
        "system": uname.system,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        "processor": uname.processor,
    }

def get_local_primary_ip(family=socket.AF_INET):
    try:
        if family == socket.AF_INET:
            remote = ("8.8.8.8", 80)
        else:
            remote = ("2001:4860:4860::8888", 80)
        s = socket.socket(family, socket.SOCK_DGRAM)
        s.connect(remote)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return None

def get_interfaces_info():
    info = {}
    if psutil:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for ifname, addr_list in addrs.items():
            rec = {"mac": None, "addrs": [], "isup": bool(stats.get(ifname).isup) if stats.get(ifname) else None}
            for a in addr_list:
                if a.family == socket.AF_INET:
                    rec["addrs"].append({"family": "IPv4", "address": a.address, "netmask": a.netmask})
                elif a.family == socket.AF_INET6:
                    rec["addrs"].append({"family": "IPv6", "address": a.address, "netmask": a.netmask})
                else:
                    mac = a.address
                    if mac and (":" in mac or "-" in mac):
                        rec["mac"] = mac
            info[ifname] = rec
    else:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                        for ele in range(0,8*6,8)][::-1])
        info["DEFAULT"] = {"mac": mac, "addrs": [{"family": "IPv4", "address": ip, "netmask": None}], "isup": None}
    return info

def get_cpu_memory_disk_info():
    if not psutil:
        return {"cpu_count": None, "memory_total": None, "disk_partitions": None}
    mem = psutil.virtual_memory()
    disks = []
    for p in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disks.append({"device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype,
                          "total": usage.total, "used": usage.used, "free": usage.free})
        except PermissionError:
            disks.append({"device": p.device, "mountpoint": p.mountpoint, "fstype": p.fstype})
    return {
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "memory_total": mem.total,
        "memory_used": mem.used,
        "memory_available": mem.available,
        "disk_partitions": disks
    }

def get_public_ip():
    if not requests:
        return None
    try:
        r = requests.get("https://api.ipify.org?format=json", timeout=2)
        if r.ok:
            return r.json().get("ip")
    except:
        return None

def print_interfaces_table(interfaces):
    table = []
    for ifname, rec in interfaces.items():
        mac = rec["mac"] or ""
        isup = rec["isup"]
        for addr in rec["addrs"]:
            table.append([ifname, mac, addr["family"], addr["address"], addr.get("netmask"), isup])
    headers = ["Interface", "MAC", "Type", "IP Address", "Netmask", "IsUp"]
    print("=== 网络接口信息 ===")
    print(tabulate(table, headers=headers, tablefmt="grid"))

def print_disk_table(disks):
    table = []
    for d in disks:
        table.append([d["device"], d.get("mountpoint",""), d.get("fstype",""),
                      d.get("total",""), d.get("used",""), d.get("free","")])
    headers = ["Device", "Mountpoint", "FSType", "Total(Bytes)", "Used(Bytes)", "Free(Bytes)"]
    print("=== 磁盘信息 ===")
    print(tabulate(table, headers=headers, tablefmt="grid"))

def main():
    print("=== 基本系统信息 ===")
    basic = get_basic_system_info()
    for k, v in basic.items():
        print(f"{k}: {v}")

    primary_ipv4 = get_local_primary_ip(socket.AF_INET)
    print(f"\n主用 IPv4: {primary_ipv4}")

    interfaces = get_interfaces_info()
    print_interfaces_table(interfaces)

    hw = get_cpu_memory_disk_info()
    print(f"\nCPU 逻辑核心数: {hw['cpu_count_logical']}, 物理核心数: {hw['cpu_count_physical']}")
    print(f"内存总量: {hw['memory_total']}, 已用: {hw['memory_used']}, 可用: {hw['memory_available']}")
    print_disk_table(hw['disk_partitions'])

    public_ip = get_public_ip()
    if public_ip:
        print(f"\n公网 IP: {public_ip}")

if __name__ == "__main__":
    main()
