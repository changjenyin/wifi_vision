#!/usr/bin/sudo /bin/bash
modprobe -r iwlwifi mac80211 cfg80211
sleep 2
modprobe iwlwifi debug=0x40000
sleep 1
ifconfig wlan0 
while [ $? -ne 0 ]
do
	ifconfig wlan0 
done
iw dev wlan0 interface add mon1 type monitor
iw mon1 set channel $1 $2
ifconfig mon1 up
