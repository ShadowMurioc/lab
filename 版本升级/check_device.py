import threading
from tools.self_upgrade import upgrade_info, check_device
from netmiko import ConnectHandler
import re
import logging
# logging.basicConfig(level=logging.DEBUG)


def process_result(success_login, alive_host, success_dev):
    global success_count
    global success_device
    global alive_device
    if success_login:
        with count_lock:
            success_count += 1
            success_device.append(success_dev)
    # 处理其他返回值，例如打印Ping测试结果
    if alive_host:
        with count_lock:
            alive_device.append(alive_host)


if __name__ == "__main__":
    info = upgrade_info(excel_name='info.xls')
    ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver = info
    # 限定并发链接数
    thread_nums = 10
    limit_thread = threading.BoundedSemaphore(value=thread_nums)
    threads = []
    success_count = 0
    success_device = []
    alive_device = []
    count_lock = threading.Lock()
    for i in range(len(info[0])):
        t1 = threading.Thread(target=lambda: process_result(*check_device(ip[i],
                                                                          hostname[i],
                                                                          user[i],
                                                                          passwd[i],
                                                                          timeout[i],
                                                                          device_type[i],
                                                                          image[i],
                                                                          sdwan_ver[i]
                                                                          )
                                                            )
                              )
        t1.start()
        threads.append(t1)
    for th in threads:
        th.join()
    print('共有<' + str(success_count) + '>台设备成功登录')
    print(str(success_device) + '台设备登录成功')
    fail_dev = []
    for dev in alive_device:
        if dev not in success_device:
            fail_dev.append(dev)
    # 判断空列表
    if fail_dev:
        # 登录交换机查看ARP 及 MAC
        device_info = {
            'device_type': 'cisco_ios',
            'ip': '172.16.180.1',
            'username': 'admin',
            'password': 'P@ssw0rd',
            'read_timeout_override': 120,
        }
        print("*" * 20 + '检查下列端口所接入的路由器' + "*" * 20)
        check_arp_mac_connect = ConnectHandler(**device_info)
        for dev in fail_dev:
            command = r'show ip arp | inc {} '.format(dev[0])
            arp = check_arp_mac_connect.send_command(command + '\n', normalize=False)
            mac_list = re.findall('\w{4}.\w{4}.\w{4}', arp)
            # for mac in mac_list:
            interface = check_arp_mac_connect.send_command('show mac address-table | inc {}'.format(mac_list[0]))
            print(interface)
        check_arp_mac_connect.disconnect()
        print("*"*20 + '检查以上端口所接入的路由器' + "*" * 20)
        ...
    print('检查以下主机：' + str(fail_dev) + '\n')
