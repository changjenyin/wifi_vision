# wifi_vision
This repository is about the example code of "WiFi Action Recognition via Vision-based Methods"
-
First, we need to record csi trace by 2 laptops with Intel 5300 NIC using Halperi's CSI tool:https://github.com/dhalperi/linux-80211n-csitool/.
(See "Code on TxRx")

After we have a data, called "test.bin", we can start extract CSI profile from it, pre-process, transform to images, extract vision-based features and train SVM classifiers to recognize the action performed.

For quick start, you can just run automate.py in new_intel_csi/parse_csi/src. e.g.

python id_automate.py WiFi_data/5g/test/ ../result/5g/test/MIMO 0 svd4H ../../imgs/5g/real/test/MIMO ../../signal_process/feature/gabor/5g/test/MIMO
---
This command means to parse CSI from .bin file in WiFi_data/5g/test/, apply SVD on 30 sub-carriers separately and save files in ../result/5g/test/MIMO, transform into 4 images and save images in ../../imgs/5g/real/test/MIMO, extract gabor features on images and save features in ../../signal_process/feature/gabor/5g/test/MIMO. 

After the whole processing, you can conduct 10-fold cross-validation by running lateFusion.py in /svm. e.g.
python lateFusion.py [if build confusion matrix, then 1] [feature directory]
---
For other parameter settings in details, please refer to automate.py in new_intel_csi/parse_csi/src.


