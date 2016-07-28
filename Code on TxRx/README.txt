This is just the example of scripts running on Tx/Rx.
You have to install the CSI toolkit https://github.com/dhalperi/linux-80211n-csitool/ on your own Tx/Rx with Intel NIC 5300.
- - - - - -

Reciever:
(in /Desktop/linux-80211n-csitool-supplementary/netlink/ directory)

./recv.sh 100 HT20 test.bin
- - - - - -

Transmitter:
(in /Desktop/linux-80211n-csitool-supplementary/injections/ directory)

./setup_inject.sh 100 HT20
./send.sh 5
