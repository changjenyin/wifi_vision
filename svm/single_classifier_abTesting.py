import re
import os
import sys
import heapq
import tempfile
import numpy as np
from lib import *
from sklearn import svm

def main():
    argc = len(sys.argv);
    if argc != 4:
        print 'Usage: python abTesting.py ifConfusion trainDir testDir'
        exit()
    
    ifConf    = sys.argv[1]
    trainDir = sys.argv[2]
    testDir   = sys.argv[3] 
    
    confPath  = os.path.join('confusionMat', 'abTesting.jpg')
    numAction = len(action_idx)
    
    # If #channel mismatches in test and train 
    channelList = os.listdir(trainDir) 
    if channelList != os.listdir(testDir):
        print 'Channel number of training in directory: ' + trainDir + ' and of testing is different!'
        exit()
    
    trainFeats = getModalFeature(trainDir)

    testFeats  = getModalFeature(testDir)
    numTestDat = len(testFeats.keys())
    print 'Number of testing data:', numTestDat, '...'

    conf_arr = np.zeros((numAction, numAction))
    probs = np.zeros((numTestDat, len(action_idx)))
    probs += getProb(testFeats, trainFeats, channelList, action_idx)
        
    success = 0
    for prob, lbl in zip(probs, testFeats.keys()) :
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

def getProb(testSet, trainSet, fileList, items):
    probs = np.zeros((len(testSet), len(items)))

    trainData = []; trainLbl = []
    for f in fileList:
        for key, val in trainSet.iteritems():
            trainData.append(val['feat'][f])
            trainLbl.append(val['lbl'])

    print len(trainLbl)
    clf = svm.SVC(probability=True, kernel='linear')
    clf.fit(trainData, trainLbl)

    for f in fileList:
        testData  = []; testLbl  = [] 
        for key, val in testSet.iteritems():
            testData.append(val['feat'][f])
            testLbl.append(val['lbl'])

        prob = clf.predict_proba(testData)
        probs += prob

    return probs/len(fileList)

if __name__ == '__main__':
    main()
