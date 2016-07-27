import os
import sys
import numpy as np
import tempfile
import shutil
from lib import *
from sklearn import cross_validation

if len(sys.argv) != 2:
    print 'Usage: python lateFusion.py img_dir'

img_dir = sys.argv[1]

instances = []; lbl = []
for f in os.listdir(img_dir):
    action = ''.join([i for i in f if not i.isdigit()])
    actionNo = action_idx[action]

    instances.append(f) 
    lbl.append(actionNo)

whole_accu = []; whole_std = []
for time in range(CV_TIMES):
    skf = cross_validation.StratifiedKFold(lbl, n_folds=KFOLD, shuffle=True) 


    accu = []
    for train_idx, test_idx in skf: 

        in_dir    = tempfile.mkdtemp()
        bof_dir   = tempfile.mkdtemp()
        test_dir  = tempfile.mkdtemp()
        train_dir = tempfile.mkdtemp()

        # Create temp directories one for training instances and the other for testing.
        for idx in train_idx:
            os.system('cp -r ' + os.path.join(img_dir, instances[idx]) + ' ' + bof_dir) 
        for idx in test_idx:
            os.system('cp -r ' + os.path.join(img_dir, instances[idx]) + ' ' + in_dir) 

        # Find centriods
        os.system('python ../signal_process/sift_bof/traverse.py ' + in_dir  + ' ' + bof_dir + ' ' + test_dir)
        os.system('python ../signal_process/sift_bof/traverse.py ' + bof_dir + ' ' + bof_dir + ' ' + train_dir)

        trainSet = getModalFeature(train_dir)
        testSet  = getModalFeature(test_dir)
    
        #prob = getProb(testSet, trainSet, os.listdir(train_dir), action_idx)
        prob = earlyFusion(testSet, trainSet, os.listdir(train_dir), action_idx)
        results = np.argmax(prob, axis=1)

        success = 0 
        for result, truth in zip(results, testSet.keys()):
            guess = reverse_ac_idx[result] 
            ans = ''.join(i for i in truth if not i.isdigit())
            if guess == ans:
                success += 1

        ac = float(success)/len(test_idx)
        print ac
        accu.append(ac)

        shutil.rmtree(in_dir)
        shutil.rmtree(bof_dir)
        shutil.rmtree(test_dir)
        shutil.rmtree(train_dir)

    accu = np.asarray(accu)
    whole_std.append(np.std(accu))
    whole_accu.append(np.mean(accu))


whole_accu = np.asarray(whole_accu)
whole_std  = np.asarray(whole_std)
print 'Accuracy:'     , np.mean(whole_accu) 
print 'Standard Dev.:', np.mean(whole_std) 
