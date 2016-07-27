# wifi_vision
Code and description of "WiFi Action Recognition via Vision-based Methods"

First, we need to record csi trace by 2 laptops with Intel 5300 NIC using Halperi's CSI tool:https://github.com/dhalperi/linux-80211n-csitool/. After we have a data, called "test.bin", we can start extract CSI profile from it, pre-process, transform to images, extract vision-based features and train SVM classifiers to recognize the action performed.
