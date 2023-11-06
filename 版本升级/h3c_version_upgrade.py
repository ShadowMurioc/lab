import threading
from netmiko import ConnectHandler
import time
from tools.self_upgrade import upgrade_info, device_login, check_device
# import logging
# logging.basicConfig(level=logging.DEBUG)


'''
配合DHCP + TFTP 完成交换机开局

DHCP CONFIGURATION SAMPLE：
system-view
dhcp enable
dhcp server ip-pool 1
    network 192.168.1.0 24
    tftp-server ip-address 192.168.1.40
    bootfile-name h3c-profile.cfg

H3C Profile 包含内容：
1. 账号密码 admin P@ssw0rd@123
2. 管理口及VLAN1 DHCP获取地址
'''


def _upgrade_device(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver):
    success_dev = check_device(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver)
    upg_device_info = device_login(ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver)
    if success_dev[2]:
        if success_dev[2][0] == upg_device_info['ip']:
            # 升级所需命令
            ftp_command = "ftp " + ftp_svr + '\n'
            ftp_username = ftp_user
            ftp_password = ftp_pass
            binary_set = 'binary'
            transfer_image_command = 'get {}'.format(image)
            ftp_close = 'bye'

            install_command = 'boot-loader file flash:/{} all main'.format(image)

            try:
                dev_conn = ConnectHandler(**upg_device_info)
                print("【{}】".format(hostname) + '  成功连接')
                time1 = time.strftime("%Y-%m-%d_%H:%M:%S")
                start = time.time()
                print("【{}】".format(hostname) + '  版本升级开始时间  ' + time1)
                print("【{}】".format(hostname) + '  正在下载镜像 =====> 【{}】'.format(image))

                transfer_image = dev_conn.send_command(ftp_command, expect_string=r':')
                transfer_image += dev_conn.send_command(ftp_username, expect_string=r'Password:')
                transfer_image += dev_conn.send_command(ftp_password, expect_string=r'ftp>')
                transfer_image += dev_conn.send_command(binary_set, expect_string=r'ftp>')
                transfer_image += dev_conn.send_command(transfer_image_command, expect_string=r'ftp>')
                transfer_image += dev_conn.send_command(ftp_close, expect_string=r'>')

                print("【{}】".format(hostname) + '  镜像已经下载完成，开始安装新版本文件=== 【{}】 ==='.format(image))
                install_image = dev_conn.send_command(install_command, expect_string=r':')
                install_image += dev_conn.send_command('Y', expect_string=r':')
                install_image += dev_conn.send_command('Y', expect_string=r':')
                install_image += dev_conn.send_command('Y', expect_string=r'>')
                print("【{}】".format(hostname) + '  新版本文件=== 【{}】 ===设置默认启动，保存配置并重启'.format(image))
                dev_conn.send_command('save f')
                reboot_cmd = dev_conn.send_command('reboot f', expect_string=r':')
                reboot_cmd += dev_conn.send_command('Y', expect_string=r'.')
                dev_conn.disconnect()
                end = time.time()
                print("【{}】".format(hostname) + '  版本升级结束时间  ' + time.strftime("%Y-%m-%d_%H:%M:%S"))
                print("【{}】".format(hostname) + '  版本升级时间持续 %.2f' % (end - start) + ' 秒')
                time.sleep(10)

            except Exception as e:
                print(ip + '  版本升级失败')


if __name__ == "__main__":
    # FTP Server 信息
    ftp_svr = '192.168.1.13'
    ftp_user = 'transfer'
    ftp_pass = "A0f3rNPgpK91"
    # 限定并发链接数

    thread_nums = 50
    limit_thread = threading.BoundedSemaphore(value=thread_nums)
    # 获取登录信息

    info = upgrade_info(excel_name='h3c_info.xls')
    ip, hostname, user, passwd, timeout, device_type, image, sdwan_ver = info

    threads = []
    for i in range(len(info[0])):
        t1 = threading.Thread(target=_upgrade_device, args=(ip[i],
                                                            hostname[i],
                                                            user[i],
                                                            passwd[i],
                                                            timeout[i],
                                                            image[i],
                                                            sdwan_ver[i],
                                                            )
                              )
        t1.start()
        threads.append(t1)
    for th in threads:
        th.join()


'''
Logging Output Sample：
【SW12】  成功连接
【SW12】  版本升级开始时间  2023-10-10_11:40:42
【SW12】  正在下载镜像 =====> 【S5130SHIG-CMW710-R8108P26.ipe】
【SW12】  镜像已经下载完成，开始安装新版本文件=== 【S5130SHIG-CMW710-R8108P26.ipe】 ===
【SW12】  新版本文件=== 【S5130SHIG-CMW710-R8108P26.ipe】 ===设置默认启动，保存配置并重启
【SW12】  版本升级结束时间  2023-10-10_11:45:35
【SW12】  版本升级时间持续 292.98 秒
'''
