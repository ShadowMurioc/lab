import pandas as pd
from netmiko import ConnectHandler


def device_info(excel_name):
    df = pd.read_excel(excel_name)
    dev_hostname_list = []
    ip_list = []
    hostname_list = []
    user_list = []
    passwd_list = []
    timeout_list = []
    device_type_list = []
    for index, row in df.iterrows():
        dev_hostname = row['hostname']
        ip = row['IP']
        hostname = row['hostname']
        user = row['username']
        passwd = row['password']
        timeout = row['timeout']
        device_type = row['platform']

        dev_hostname_list.append(dev_hostname)
        ip_list.append(ip)
        hostname_list.append(hostname)
        user_list.append(user)
        passwd_list.append(passwd)
        timeout_list.append(timeout)
        device_type_list.append(device_type)

    return dev_hostname_list, ip_list, hostname_list, user_list, passwd_list, timeout_list, device_type_list


def device_login(ip, user, passwd, timeout, device_type, session_log=None):
    device_ssh = {
        'device_type': device_type,
        'ip': ip,
        'username': user,
        'password': passwd,
        'read_timeout_override': timeout,
        'session_log': session_log,
    }
    device_session = ConnectHandler(**device_ssh)
    return device_session


def parse_interface_info(excel_name, dtype=str):
    df = pd.read_excel(excel_name, dtype=dtype)
    hostname_list = []
    device_type_list = []
    interface_name_list = []
    pc_list = []
    pcid_list = []
    link_type_list = []
    vlan_list = []
    ip_list = []
    desc_list = []
    for index, row in df.iterrows():
        hostname = row['hostname']
        device_type = row['platform']
        interface_name = row['interface_name']
        portchannel = row['portchannel']
        portchannel_id = str(row['portchannel_id'])
        link_type = row['link_type']
        vlan = row['vlan']
        ip = row['ip']
        description = row['description']

        hostname_list.append(hostname)
        device_type_list.append(device_type)
        interface_name_list.append(interface_name)
        pc_list.append(portchannel)
        pcid_list.append(portchannel_id)
        link_type_list.append(link_type)
        vlan_list.append(vlan)
        ip_list.append(ip)
        desc_list.append(description)
    return hostname_list, device_type_list, interface_name_list, pc_list, \
           pcid_list, link_type_list, vlan_list, ip_list, desc_list
