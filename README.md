# Install Kismet
## Qinghua Source
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
** if anything wrong with libwebsockets**, please refer to [kismet on raspberry pi failed ./configure libwebsockets](https://stackoverflow.com/questions/64759406/kismet-on-raspberry-pi-failed-configure-libwebsockets)
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
## Remove Kismet
1. if you installed from a Kismet package in your distribution:

```
sudo apt remove kismet kismet-plugins
```

2. If you installed Kismet from source yourself

```
$ sudo rm -rfv /usr/local/bin/kismet* /usr/local/share/kismet* /usr/local/etc/kismet*
```

## Config Kismet
### path of config files

1. when compiling from source

```
/usr/local/etc/
```

2. when installing from the Kismet packages

```
/etc/kismet/
```

### Register user accout and password at the 1st time access to kismet web `http://localhost:2501`
* we set default user:pass as **kismet:kismet**
* files `kismet_httpd.conf` and `session.db` will be generated at directory `~/.kismet`, the content of `kismet_httpd.con' will be like:

```
httpd_password=kismet
httpd_username=kismet
```

### clear old device data
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

## Datasource and channel hopping
1. add datasource in `kismet.conf` under `/usr/local/etc/` when compiling from source, or `/etc/kismet/` when installing from the Kismet packages.

```
source=[interface]:[option, option, option]
#like:
#source=wlan1
```

2. kismet defaultly supports wifi channel hopping, and you can even set the hopping time 'channel_hop_speed=channels/sec | channels/min' and split popping `split_source_hopping=true` for multi wifi interface, see [https://www.kismetwireless.net/docs/readme/datasources/]()

# Install Kismet with support of Ubertooth
## Install build tools and dependencies
**note: no need to install libbtbb-dev, we will build it from source latter**
```
sudo apt-get -y update
sudo apt install build-essential git libwebsockets-dev pkg-config zlib1g-dev libnl-3-dev libnl-genl-3-dev libcap-dev libpcap-dev libnm-dev libdw-dev libsqlite3-dev libprotobuf-dev libprotobuf-c-dev protobuf-compiler protobuf-c-compiler libsensors4-dev libusb-1.0-0-dev python3 python3-setuptools python3-protobuf python3-requests python3-numpy python3-serial python3-usb python3-dev python3-websockets librtlsdr0 
```

## Get and build libbtbb
```
cd ~
wget https://github.com/greatscottgadgets/libbtbb/archive/2020-12-R1.tar.gz -O libbtbb-2020-12-R1.tar.gz
tar xf libbtbb-2020-12-R1.tar.gz
cd libbtbb-2020-12-R1
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```
## Get and build Ubertooth tools
```
cd ~
wget https://github.com/greatscottgadgets/ubertooth/releases/download/2020-12-R1/ubertooth-2015-10-R1.tar.xz -O ubertooth-2020-12-R1.tar.xz
tar xf ubertooth-2020-12-R1.tar.xz
cd ubertooth-2020-12-R1/host
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```

## get and build Kismet with ubertooth from source
### build kismet from source, refer the first section to install the dependencies
[refer](https://kismetwireless.net/docs/readme/quickstart/#compiling-quick-setup)
**check if Ubertooth One: yes after ./configure**

### Get and build Kismet and Ubertooth plugin
```
cd ~
wget http://www.kismetwireless.net/code/kismet-2016-01-R1.tar.xz
tar xf kismet-2016-01-R1.tar.xz
cd kismet-2016-01-R1
ln -s ../ubertooth-2015-10-R1/host/kismet/plugin-ubertooth ./
./configure
make deb
make && make plugins
make suidinstall
make plugins-install

#Set writeinterval
sed -i "s/writeinterval=300/writeinterval=10/g" /usr/local/etc/kismet.conf
```

# Development
## Environment
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
4. kafuka and redis
```
pip install kafka-python==2.0.1
pip install redis
```

# make the sniffer.py as service
## nano wifi_sniffer.servcie
```
[Unit]
Description=Wifi Sniffer Service
After=multi-user.target

[Service]
Type=idle
User=pi
ExecStart=/usr/bin/python3 /home/pi/projects/wifi_sniffer/sniffer.py > /home/pi/projects/wifi_sniffer.log 2>&1
Restart=always

[Install]
WantedBy=multi-user.target
```

** key: need to add 'User=pi', otherwise, the module Kismest_rest will not be loaded **


## Steps to start service

```
$ cd project_dir
$ sudo cp wifi_sniffer.service /lib/systemd/system/wifi_sniffer.service
$ sudo chmod 644 /lib/systemd/system/wifi_sniffer.service
$ sudo systemctl daemon-reload
$ sudo systemctl enable wifi_sniffer.service
$ sudo systemctl start wifi_sniffer.service
```
