# wifi_vision
Description
------
This repository is about the example code of "WiFi Action Recognition via Vision-based Methods" published on IEEE ICASSP 2016 and "Location-Independent WiFi Action Recognition via Vision-based Methods" published on ACM MM 2016.

Collect and Process CSI
------
First, we need to record csi trace by 2 laptops with Intel 5300 NIC using Halperi's CSI tool:https://github.com/dhalperi/linux-80211n-csitool/.
(See "Code on TxRx")

After we have a data, called "test.bin", we can start extract CSI profile from it, pre-process, transform to images, extract vision-based features and train SVM classifiers to recognize the action performed.

For quick start, you can just run automate.py in parse_csi/src. e.g.

python id_automate.py test/ ../result/test/ 0 svd4H ../../imgs/test/ ../../signal_process/feature/gabor/test/

This command means to parse CSI from .bin files in test/, apply SVD on 30 sub-carriers separately and save files in ../result/test/, transform into 4 images and save images in ../../imgs/test/, extract gabor features on images and save features in ../../signal_process/feature/gabor/test/. Note that you may have to create the empty directory for files.

Evaluation
------
After the whole processing, you can conduct 10-fold cross-validation by running lateFusion.py in /svm. e.g.
python lateFusion.py [if build confusion matrix, then 1] [feature directory]

Also, if you want to do cross-room testing, process data traces from two different rooms and save in room1/, room2/, 
place them as abTesting/train/gabor/room1, abTesting/test/gabor/room2, 
meaning train linear SVM on room1/ and testing data from room2/. Then run abTesting.py in /svm. e.g.

python abTesting.py [if build confusion matrix, then 1] [abTesting folder]

Others
---
For other parameter settings in details, please refer to automate.py in parse_csi/src.
