### Install Kismet
##Qinghua Source
1. /etc/apt/sources.list
```
注释掉已配置好的raspberry官方镜像，使用#号注释(或直接删除，哈哈)

添加清华源镜像：

deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main contrib non-free rpi

deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main contrib non-free rpi
```
2. sudo vim /etc/apt/sources.list.d/raspi.list
```
注释掉原内容，并以以下内容替换：

deb http://mirror.tuna.tsinghua.edu.cn/raspberrypi/ stretch main ui

deb-src http://mirror.tuna.tsinghua.edu.cn/raspberrypi/ stretch main ui
```

## Build
1. audo apt-get update

2. install needed packages
```
$ sudo apt install build-essential git libmicrohttpd-dev pkg-config zlib1g-dev libnl-3-dev libnl-genl-3-dev libcap-dev libpcap-dev libnm-dev libdw-dev libsqlite3-dev libprotobuf-dev libprotobuf-c-dev protobuf-compiler protobuf-c-compiler libsensors4-dev libusb-1.0.0-dev python3 python3-setuptools python3-protobuf python3-requests python3-numpy python3-serial python3-usb python3-dev librtlsdr0 libubertooth-dev libbtbb-dev 
```

3. build
```
$ cd /kismet
$ ./configure
$ make -j4
```

4. install
```
$ sudo make suidinstall
```

5. Add your user to the kismet group
```
$ sudo usermod -aG kismet $USER
#logout, and login, check
$groups
```
###Remove Kismet
1. if you installed from a Kismet package in your distribution:
```
sudo apt remove kismet kismet-plugins
```
2. If you installed Kismet from source yourself
```
$ sudo rm -rfv /usr/local/bin/kismet* /usr/local/share/kismet* /usr/local/etc/kismet*
```

###Config Kismet
#path of config files
1. when compiling from source
```
/usr/local/etc/
``
2. when installing from the Kismet packages
```
/etc/kismet/
```

# Register user accout and password at the 1st time access to kismet web `http://localhost:2501`
1. we set default user:pass as **kismet:kismet**
2. files `kismet_httpd.conf` and `session.db` will be generated at directory `~/.kismet`, the content of `kismet_httpd.con' will be like:
```
httpd_password=kismet
httpd_username=kismet
```
# clear old device data
there is a config parameter `persistent_timeout` in configure file `kismet_storage.conf` to drop old data, its defualt value is 86400(one day) 

## Start as a service
1. Kismet can also be started as a service; typically in this usage you should also pass --no-ncurses to prevent the ncurses wrapper from loading
2. An example systemd script is in the packaging/systemd/ directory of the Kismet source; if you are installing from source this can be copied to /etc/systemd/system/kismet.service, and packages should automatically include this file.
3. When starting Kismet via systemd, you should install kismet as suidroot, and use systemctl edit kismet.service to set the following:
```
[Service]
User=your-unprivileged-user
Group=kismet
```
4. **remeber** to `sudo systemctl enable kismet`

##Datasource and channel hopping
1. add datasource in `kismet.conf` under `/usr/local/etc/` when compiling from source, or `/etc/kismet/` when installing from the Kismet packages.
```
source=[interface]:[option, option, option]
#like:
#source=wlan1
```
2. kismet defaultly supports wifi channel hopping, and you can even set the hopping time 'channel_hop_speed=channels/sec | channels/min' and split popping `split_source_hopping=true` for multi wifi interface, see [https://www.kismetwireless.net/docs/readme/datasources/]()



###Development
##Environment
1. kismet_rest 
    * pip
```
$ pip install kismet_rest
```
    * build src
```
$ git clone https://github.com/kismetwireless/python-kismet-rest
$ cd python-kismet-rest && pip install .
```

2. timeloop
refer: [https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679](An elegant way to run periodic tasks in python), [https://github.com/sankalpjonn/timeloop](github)
```
pip install timeloop
```
3. influxdb for python3
```
sudo apt-get install python3-influxdb
```
