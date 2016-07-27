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
featDirs.append(sys.argv[2])
output_file = open(sys.argv[3], 'a')
output_result = action_idx
output_result = dict.fromkeys(output_result, 0)

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

numAction = len(action_idx)
actionFeats = {}
for featDir in featDirs:
    actionFeats[featDir] = getModalFeature(featDir)

keys  = actionFeats[featDirs[0]].keys()
label = [actionFeats[featDirs[0]][key]['lbl'] for key in keys]

conf_arr = np.zeros((numAction, numAction))
whole_accu = []; whole_std = []
eachActionCnt = 0
for time in range(CV_TIMES):
    skf = cross_validation.StratifiedKFold(label, n_folds=KFOLD, shuffle=True) 
    
    accu = []; 
    for train_idx, test_idx in skf:
        if eachActionCnt == 0:
            eachActionCnt = (len(train_idx) + len(test_idx)) / numAction
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

        success = 0 
        for result, truth in zip(results, testSet.keys()):
            guess = reverse_ac_idx[result] 
            ans = re.search('([\D]+)\d+', truth).group(1)
            #if ans != guess:
            #    print ans + ' -> ' + guess
            if guess == ans:
                success += 1
                output_result[ans] += 1

            conf_arr[action_idx[ans]][result] += 1

        ac = float(success)/len(testName)
        accu.append(ac)

    accu = np.asarray(accu)
    whole_std.append(np.std(accu))
    whole_accu.append(np.mean(accu))

if ifConf == '1':
    confusionMatrix(conf_arr/(CV_TIMES*KFOLD), [reverse_ac_idx[ac_idx][0] for ac_idx in range(numAction)], os.path.join('confusionMat', confPath + '.jpg'))

whole_accu = np.asarray(whole_accu)
whole_std  = np.asarray(whole_std)
print 'Accuracy:'     , np.mean(whole_accu) 
print 'Standard Dev.:', np.mean(whole_std) 

# Write separated results to Fig/
names = featDirs[0].split('/')
name = []
if names[-1] == "":
    name = names[-2]
else:
    name = names[-1]
output_file.write("%s " % name)

output_result = {k: v * (1.0 / eachActionCnt) for k, v in output_result.items()}
for value in output_result.values():
    output_file.write("%s " % value)
output_file.write("%s" % np.mean(whole_accu))
output_file.write("\n")
output_file.close()
