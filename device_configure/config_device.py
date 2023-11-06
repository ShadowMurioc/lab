from tools.dev_info import device_login, device_info, parse_interface_info
from jinja2 import Template
# import logging
# logging.basicConfig(level=logging.DEBUG)


def genrate_interface_config(hostname, device_type, interface_name, pc, pcid, link_type, vlan, ip, desc):
    if device_type in ['cisco_ios', '思科']:
        template_name = 'cisco_switch_config_interface.j2'
        with open(template_name) as file:
            template_content = file.read()
    elif device_type in ['huawei', '华为']:
        template_name = 'huawei_switch_config_interface.j2'
        with open(template_name) as file:
            template_content = file.read()
    j2_template = Template(template_content)
    data = {
        'hostname': hostname,
        'device_type': device_type,
        'interface_name': interface_name,
        'pc': pc,
        'pcid': str(pcid),
        'link_type': link_type,
        'vlan': vlan,
        'ip': ip,
        'desc': str(desc)
    }

    config_info = j2_template.render(data)
    new_config = {'hostname': hostname,
                  'config': config_info
                  }
    return new_config


def process_rst(data):
    parse_device_info = device_info(excel_name='info.xls')
    interfaces = {hostname: [] for hostname in hostnames}
    for item in data:
        hostname = item['hostname']
        if hostname in interfaces:
            interfaces[hostname].append(item['config'])
    for hostname, interface_list in interfaces.items():
        small_list = [item.split('\n') for item in interface_list]
        for i in range(len(parse_device_info[0])):
            if hostname == parse_device_info[0][i]:
                try:
                    dev_conn = device_login(ip=parse_device_info[1][i],
                                            user=parse_device_info[3][i],
                                            passwd=parse_device_info[4][i],
                                            timeout=parse_device_info[5][i],
                                            device_type=parse_device_info[6][i],
                                            session_log='session.log'
                                            )
                    if not dev_conn.check_enable_mode():
                        dev_conn.enable()
                    print(f"{hostname}接口配置:")

                    print("*" * 100)
                    for interface in interface_list:
                        print(interface)
                    ans = input('Warning：配置由Excel中所填内容自动生成，\n'
                                '         确认无误后再进行下一步操作,请输入【Y/N】:')
                    print("*" * 100)

                    while ans not in ['Y', 'y', 'N', 'n', 'YES', 'YES', 'NO', 'NO']:
                        ans = input('Warning：配置由Excel中所填内容自动生成，\n'
                                    '         确认无误后再进行下一步操作,请输入【Y/N】:')

                    if ans == 'Y' or ans == 'y':
                        print('connecting to ' + hostname)
                        for data in small_list:
                            config_info = dev_conn.send_config_set(config_commands=data)
                            print(config_info)
                        dev_conn.disconnect()
                        print("*" * 100)
                    elif ans == 'N' or ans == 'n':
                        pass

                except Exception as e:
                    print('connecting to ' + hostname + ' failed')


if __name__ == "__main__":
    parse_interface = parse_interface_info(excel_name='interface_info.xls')
    # parse_interface = parse_interface_info(excel_name='a12.xls')
    hostname, device_type, interface_name, pc, pcid, link_type, vlan, ip, desc = parse_interface
    hostnames = hostname
    all_data = []
    for i in range(len(hostname)):
        data = genrate_interface_config(hostname[i],
                                        device_type[i],
                                        interface_name[i],
                                        pc[i],
                                        pcid[i],
                                        link_type[i],
                                        vlan[i],
                                        ip[i],
                                        desc[i]
                                        )
        all_data.append(data)
    process_rst(all_data)
