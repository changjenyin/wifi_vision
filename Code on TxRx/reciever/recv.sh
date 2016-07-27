ip link set wlan0 down
sleep 2
../injection/setup_monitor_csi.sh $1 $2

echo 'Initiating colletion of csi...'
nice -n -20 ./log_to_file $3
