# -*-coding:utf-8-*-

import pywifi, time
from pywifi import const

# 1、python连接WiFi，需要使用pywifi包，安装pywifi：pip install pywifi
#注意：如果提示找不到comtypes，则还需要安装pip install comtypes
# 2、判断wifi连接状态：
def wifi_connect_status():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[1]  # acquire the first Wlan card,maybe not

    if iface.status() in [const.IFACE_CONNECTED, const.IFACE_INACTIVE]:
        print("wifi connected!")
        return 1
    else:
        print("wifi not connected!")
    return 0


# 3、扫描wifi：
def scan_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    time.sleep(1)
    basewifi = iface.scan_results()

    for i in basewifi:
        print("wifi scan result:{}".format(i.ssid))
        print("wifi device MAC address:{}".format(i.bssid))
    return basewifi

# 4、连接指定的wifi：
def connect_wifi():
    wifi = pywifi.PyWiFi()
    ifaces = wifi.interfaces()[1]
    print(ifaces.name())  # 输出无线网卡名称
    ifaces.disconnect()
    time.sleep(3)

    profile = pywifi.Profile()  # 配置文件
    profile.ssid = "LH_IoT"  # wifi名称
    profile.auth = const.AUTH_ALG_OPEN  # 需要密码
    profile.akm.append(const.AKM_TYPE_WPA2PSK)  # 加密类型
    profile.cipher = const.CIPHER_TYPE_CCMP  # 加密单元
    profile.key = "gogogo123"  # wifi密码

    ifaces.remove_all_network_profiles()  # 删除其它配置文件
    tmp_profile = ifaces.add_network_profile(profile)  # 加载配置文件
    ifaces.connect(tmp_profile)
    time.sleep(5)
    isok = True

    if ifaces.status() == const.IFACE_CONNECTED:
        print("connect successfully!")
    else:
        print("connect failed!")
    time.sleep(1)
    return isok

#5、测试
def main():
    print("start")
    wifi_connect_status()
    scan_wifi()
    connect_wifi()
    print("finish!")

if __name__ == "__main__":
    main()
