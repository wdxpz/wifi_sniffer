##kismet zigbee sources
 
* [official supported sources](https://www.kismetwireless.net/docs/readme/datasources_802154/#802154-zigbee)
* cli command
```
kismet -c ticc2531-0
```
## zigbee addressing 64bit and 16bit
1. [Addressing](https://www.digi.com/resources/documentation/Digidocs/90002002/Concepts/c_zb_addressing.htm?TocPath=Transmission%2C%20addressing%2C%20and%20routing%7C_____1)
2. [Understanding Zigbee and Wireless Mesh Networking](https://www.blackhillsinfosec.com/understanding-zigbee-and-wireless-mesh-networking/)

##  data package analysis
[Sniff Zigbee traffic](https://www.zigbee2mqtt.io/advanced/zigbee/04_sniff_zigbee_traffic.html#_1-flashing-the-cc2531-stick)
```
wireshark -k -i <( /usr/local/bin/whsniff -c 11 )
```

## valuable kismet keys
```
kismet.device.base.macaddr: "70:16",
kismet.device.base.signal:kismet.common.signal.last_signal: -70,
kismet.device.base.signal:kismet.common.signal.signal_rrd:kismet.common.rrd.last_time: 1652432508,
kismet.device.base.last_time: 1652432499,


kismet.device.base.last_time``,
                ``kismet.device.base.macaddr``,
                ``kismet.device.base.manuf``,
                ``kismet.device.base.mod_time``,
                ``kismet.device.base.name``
`kismet.device.base.phyname`
```
