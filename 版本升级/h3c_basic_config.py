import threading
from netmiko import ConnectHandler
from tools.self_upgrade import upgrade_info, device_login
from jinja2 import Template

# import time
# import logging
# logging.basicConfig(level=logging.DEBUG)`


def _config_device(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver):
    template_name = 'baseline.j2'
    with open(template_name) as file:
        template_content = file.read()
    j2_template = Template(template_content)
    data = {
        'cfg_hostname': hostname,
        'sdwan_ver': sdwan_ver,
        'model': image,
        'Location': 'Shanghai DZZG',
    }
    config_info = j2_template.render(data)

    if data['cfg_hostname'] == hostname:
        try:
            device_info = device_login(ip, hostname, user, passwd, timeout, device_type)
            dev_conn = ConnectHandler(**device_info)
            dev_conn.send_config_set(config_info)
            dev_conn.disconnect()
            print(hostname + '配置完成')

        except Exception as e:
            print(hostname + '配置出现问题，手动检查')


if __name__ == "__main__":
    # 限定并发链接数
    thread_nums = 50
    limit_thread = threading.BoundedSemaphore(value=thread_nums)
    # 获取登录信息

    info = upgrade_info(excel_name='h3c_info.xls')
    ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver = info

    threads = []
    for i in range(len(info[0])):
        t1 = threading.Thread(target=_config_device, args=(ip[i],
                                                           hostname[i],
                                                           user[i],
                                                           passwd[i],
                                                           timeout[i],
                                                           device_type[i],
                                                           image[i],
                                                           sdwan_ver[i],
                                                           )
                              )
        t1.start()
        threads.append(t1)
    for th in threads:
        th.join()
