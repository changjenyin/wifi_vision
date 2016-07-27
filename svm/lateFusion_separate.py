import re
import os
import sys
import numpy as np
from lib import *
from sklearn import cross_validation

if len(sys.argv) < 3:
    print 'Usage: python lateFusion.py ifConfusion featDir1 featDir2 ...'

ifConf = sys.argv[1]
featDirs = []
for i in range(2, len(sys.argv)):
    featDirs.append(sys.argv[i])
numAction = len(action_idx)

confPath =''
for featDir in featDirs:
    names = featDir.split('/')
    if confPath == '' and names[-1] == '':
        confPath = names[-2] 
    elif confPath == '' and names[-2] == '':
        confPath = names[-1]
    elif names[-1] == '':
        confPath = confPath + '_' + names[-2]
    else:
        confPath = confPath + '_' + names[-1]

actionFeats = {}
for featDir in featDirs:
    actionFeats[featDir] = getModalFeature(featDir)

keys  = actionFeats[featDirs[0]].keys()
label = [actionFeats[featDirs[0]][key]['lbl'] for key in keys]

conf_arr = np.zeros((numAction, numAction))
whole_accu = []; whole_std = []
ryan_whole_accu = []; ryan_whole_std = []
rest_whole_accu = []; rest_whole_std = []
for time in range(CV_TIMES):
    skf = cross_validation.StratifiedKFold(label, n_folds=KFOLD, shuffle=True) 
    
    ryan_accu = []
    rest_accu = []
    accu = []
    for train_idx, test_idx in skf:
        testName = [keys[idx] for idx in test_idx]
        probs = np.zeros((len(testName), numAction))

        for featDir in featDirs:
            testSet  = {}
            trainSet = {}
            for name in keys:
                if name in testName:
                    testSet[name]  = actionFeats[featDir][name]
                else:
                    trainSet[name] = actionFeats[featDir][name]
    
            prob = getProb(testSet, trainSet, os.listdir(featDir), action_idx)
            probs += prob

        results = np.argmax(probs, axis=1)

        ryan_success = 0
        rest_success = 0
        success = 0 
        for result, truth in zip(results, testSet.keys()):
            guess = reverse_ac_idx[result] 
            ans = re.search('([\D]+)\d+', truth).group(1)
            if ans != guess:
                print ans + ' -> ' + guess
            if guess == ans:
                success += 1
                if ans == 'ryan':
                    ryan_success += 1
                else:
                    rest_success += 1

            conf_arr[action_idx[ans]][result] += 1

        ac = float(success)/len(testName)
        accu.append(ac)
        ac = float(ryan_success)
        ryan_accu.append(ac)
        ac = float(rest_success)/(len(testName) - 1)
        rest_accu.append(ac)


    accu = np.asarray(accu)
    whole_std.append(np.std(accu))
    whole_accu.append(np.mean(accu))
    ryan_accu = np.asarray(ryan_accu)
    ryan_whole_std.append(np.std(ryan_accu))
    ryan_whole_accu.append(np.mean(ryan_accu))
    rest_accu = np.asarray(rest_accu)
    rest_whole_std.append(np.std(rest_accu))
    rest_whole_accu.append(np.mean(rest_accu))

if ifConf == '1':
    confusionMatrix(conf_arr/(CV_TIMES*KFOLD), [reverse_ac_idx[ac_idx][0] for ac_idx in range(numAction)], os.path.join('confusionMat', confPath + '.jpg'))

print '\n'
whole_accu = np.asarray(whole_accu)
whole_std  = np.asarray(whole_std)
print 'Accuracy:'     , np.mean(whole_accu) 
print 'Standard Dev.:', np.mean(whole_std) 
ryan_whole_accu = np.asarray(ryan_whole_accu)
ryan_whole_std  = np.asarray(ryan_whole_std)
print 'ryan Accuracy:'     , np.mean(ryan_whole_accu) 
print 'ryan Standard Dev.:', np.mean(ryan_whole_std) 
rest_whole_accu = np.asarray(rest_whole_accu)
rest_whole_std  = np.asarray(rest_whole_std)
print 'rest Accuracy:'     , np.mean(rest_whole_accu) 
print 'rest Standard Dev.:', np.mean(rest_whole_std) 
