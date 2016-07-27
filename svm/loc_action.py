import os
import sys
import numpy as np
from lib import *
from sklearn import cross_validation

if len(sys.argv) != 2:
    print 'Usage: python lateFusion.py featDir'

featDir = sys.argv[1]
numAction = len(action_idx)

names = featDir.split('/')
if names[-1] == '':
    confPath = names[-2] 
else:
    confPath = names[-1]

actionFeats = {}
locationFeats = {}
motionFeats = {}
motion_cnt = {key: 0 for key in action_idx.iterkeys()}
location_cnt = {key: 0 for key in location_idx.iterkeys()}

motion_map = {}
location_map = {}
loc_motion_map = {}

actionFeats = getModalFeature(featDir)
locationFeats = {}
motionFeats = {}

for key, val in actionFeats.iteritems():
    loc, action = key.split('_')
    action = ''.join([i for i in action if not i.isdigit()])

    location_cnt[loc] += 1
    motion_cnt[action] += 1

    new_loc = loc + str(location_cnt[loc])
    new_action = action + str(motion_cnt[action])

    motion_map[key] = new_action
    location_map[key] = new_loc
    loc_motion_map[new_loc] = new_action

    locationFeats[new_loc] = {}
    locationFeats[new_loc]['feat'] = val['feat']
    locationFeats[new_loc]['lbl'] = location_idx[loc]

    motionFeats[new_action] = {}
    motionFeats[new_action]['feat'] = val['feat']
    motionFeats[new_action]['lbl'] = action_idx[action]
    motionFeats[new_action]['loc'] = location_idx[loc]

keys  = actionFeats.keys()
label = [actionFeats[key]['lbl'] for key in keys]

conf_arr = np.zeros((numAction, numAction))
whole_accu = []; whole_std = []
whole_loc_accu = []; whole_loc_std = []
for time in range(CV_TIMES):
    skf = cross_validation.StratifiedKFold(label, n_folds=KFOLD, shuffle=True) 
    
    accu = []
    loc_accu = []
    # Construct location classifier
    for train_idx, test_idx in skf: 
        locTestName = [location_map[keys[idx]] for idx in test_idx]
        acTestName  = [motion_map[keys[idx]] for idx in test_idx]
        probs = np.zeros((len(locTestName), len(location_idx)))

        locTestSet  = {}
        locTrainSet = {}
        acTrainSet  = {}
        acTestSet   = {}
        for name in keys:
            loc_name = location_map[name]
            ac_name  = motion_map[name]
            if loc_name in locTestName:
                locTestSet[loc_name]  = locationFeats[loc_name]
            else:
                locTrainSet[loc_name] = locationFeats[loc_name]

            if ac_name in acTestName:
                acTestSet[ac_name]  = motionFeats[ac_name]
            else:
                acTrainSet[ac_name] = motionFeats[ac_name]
        
        prob = getProb(locTestSet, locTrainSet, os.listdir(featDir), location_idx)
        probs += prob

        # construct action classifiers
        classifiers = consClassifiers(acTrainSet, os.listdir(featDir), location_idx)

        results = np.argmax(probs, axis=1)

        success = 0 
        loc_success = 0
        for result, truth in zip(results, locTestSet.keys()):
            action_key = loc_motion_map[truth]
            guess_loc = reverse_loc_idx[result] 

            if reverse_loc_idx[result] == ''.join([i for i in truth if not i.isdigit()]):
                loc_success += 1

            probs = predictAction(classifiers[guess_loc], motionFeats[action_key], os.listdir(featDir))
            guess_action = np.argmax(probs) 
            if guess_action == motionFeats[action_key]['lbl']:
                success += 1

        ac = float(success)/len(locTestName)
        accu.append(ac)

        loc_ac = float(loc_success)/len(locTestName)
        loc_accu.append(loc_ac)

    accu = np.asarray(accu)
    loc_accu = np.asarray(loc_accu)

    whole_std.append(np.std(accu))
    whole_accu.append(np.mean(accu))

    whole_loc_std.append(np.std(loc_accu))
    whole_loc_accu.append(np.mean(loc_accu))

whole_accu = np.asarray(whole_accu)
whole_std  = np.asarray(whole_std)
whole_loc_accu = np.asarray(whole_loc_accu)
whole_loc_std  = np.asarray(whole_loc_std)

print 'Accuracy:'     , np.mean(whole_accu) 
print 'Standard Dev.:', np.mean(whole_std) 
print 'Location Accuracy:'     , np.mean(whole_loc_accu) 
print 'Location Standard Dev.:', np.mean(whole_loc_std) 
