import re
import os
import sys
import heapq
import numpy as np
from lib import *
from sklearn import svm

if len(sys.argv) != 3:
    print 'Usage: python abTesting.py ifConfusion abDir'
    exit()

ifConf    = sys.argv[1]
abDir     = sys.argv[2]
trainDir  = os.path.join(abDir, 'train')
testDir   = os.path.join(abDir, 'test')

confPath  = os.path.join('confusionMat', 'abTesting.jpg')
numAction = len(action_idx)

modality   = os.listdir(trainDir)
numTestDat = 0
trainFeats = {}; testFeats = {}; channelList = {}
for modal in modality:
    path = os.path.join(trainDir, modal)

    # If #channel mismatches in certain modality
    channelList[modal] = os.listdir(path) 
    if channelList[modal] != os.listdir(os.path.join(testDir, modal)):
        print 'Directory:', modal, ' Channel number of training and of testing is different!'
        exit()

    trainFeats[modal] = getModalFeature(os.path.join(trainDir, modal))
    testFeats[modal]  = getModalFeature(os.path.join(testDir,  modal))
    
    # Check if #testdata is coherent in each modality
    if numTestDat == 0:
        numTestDat = len(testFeats[modal].keys())
    if numTestDat != len(testFeats[modal].keys()):
        print 'Number of testdata mismathces in', os.path.join(testDir, modal)

print 'Number of testing data:', numTestDat, '...'

conf_arr = np.zeros((numAction, numAction))
probs = np.zeros((numTestDat, len(action_idx)))
for modal in modality: 
    probs += getProb(testFeats[modal], trainFeats[modal], channelList[modal], action_idx)
    
success = 0
for prob, lbl in zip(probs, testFeats[modal].keys()) :
    ans = re.search('([\D]+)\d+', lbl).group(1)
    result  = reverse_ac_idx[np.argmax(prob)]

    second_largest = heapq.nlargest(2, prob)[1]
    result2 = reverse_ac_idx[np.where(prob == second_largest)[0][0]]
    print ans + ' -> ' + result + ' -> ' + result2 
    conf_arr[action_idx[ans]][action_idx[result]] += 1
    if result == ans:
        success += 1

if ifConf == '1':
    confusionMatrix(conf_arr, [reverse_ac_idx[ac_idx] for ac_idx in range(numAction)], confPath)

print float(success) / numTestDat
