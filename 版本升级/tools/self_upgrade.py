import pandas as pd
import ping3
import netmiko
from netmiko import ConnLogOnly, ConnectHandler


def upgrade_info(excel_name):
    df = pd.read_excel(excel_name)
    ip_list = []
    hostname_list = []
    user_list = []
    passwd_list = []
    timeout_list = []
    device_type_list = []
    image_list = []
    sdwan_ver_list = []
    for index, row in df.iterrows():
        ip = row['IP']
        hostname = row['hostname']
        user = row['username']
        passwd = row['password']
        timeout = row['timeout']
        device_type = row['platform']
        image = row['image_file']
        sdwan_ver = row['sdwan_ver']

        ip_list.append(ip)
        hostname_list.append(hostname)
        user_list.append(user)
        passwd_list.append(passwd)
        timeout_list.append(timeout)
        device_type_list.append(device_type)
        image_list.append(image)
        sdwan_ver_list.append(sdwan_ver)

    return ip_list, hostname_list, user_list, passwd_list, timeout_list, device_type_list, image_list, sdwan_ver_list


def device_login(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver):
    device_ssh = {
       'device_type': device_type,
       'ip': ip,
       'username': user,
       'password': passwd,
       'read_timeout_override': timeout,
       'session_log': 'session.log',
    }
    return device_ssh


def check_device(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver):
    rst = ping3.ping(ip)
    n = 0
    success_login = False
    alive_host = []
    success_dev = []
    if rst:
        alive_host.append(ip)
        # print(hostname + ' is alive')
        check_device_info = device_login(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver)
        try:
            # 消耗内存
            # check_netconnect = ConnectHandler(**check_device_info)
            # 链接失败时，需要到日志内进行查询
            check_netconnect = ConnLogOnly(**check_device_info)
            if check_netconnect:
                success_login = True
                success_dev.append(ip)
                n += 1
            else:
                ...
                # print(ip + ' login failed')
            # check_netconnect.disconnect()
        # exception 配合ConnectHandler进行使用
        except netmiko.exceptions.NetmikoAuthenticationException as e:
            print(ip + ' login failed')
        except netmiko.exceptions.NetmikoTimeoutException as e:
            print(ip + ' timeout')
        except Exception as e:
            print(e)
    else:
        pass
    return success_login, alive_host, success_dev
