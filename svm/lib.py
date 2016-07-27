import os 
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from sklearn import svm

KFOLD = 10
CV_TIMES = 1
NUM_ANT_PAIR = 4

#action_idx     = {'box':0, 'clap':1, 'empty':2, 'jog':3, 'run':4, 'walk':5, 'wave':6}
#reverse_ac_idx = {0:'box', 1:'clap', 2:'empty', 3:'jog', 4:'run', 5:'walk', 6:'wave'}
action_idx      = {'still':0, 'jump':1, 'pickbox':2, 'run':3, 'swing':4, 'walk':5}
reverse_ac_idx  = {0:'still', 1:'jump', 2:'pickbox', 3:'run', 4:'swing', 5:'walk'}
#action_idx      = {'still':0, 'run':1, 'walk':2}
#reverse_ac_idx  = {0:'still', 1:'run', 2:'walk'}
#action_idx = {'ceci':0, 'eric':1, 'hoon':2, 'jacky':3, 'mansion':4, 'peter':5, 'ryan':6, 'shuen':7, 'smallblue':8, 'wally':9, 'longtshirt':10, 'suit':11, 'coat':12}
#reverse_ac_idx  = {0:'ceci', 1:'eric', 2:'hoon', 3:'jacky', 4:'mansion', 5:'peter', 6:'ryan', 7:'shuen', 8:'smallblue', 9:'wally', 10:'longtshirt', 11:'suit', 12:'coat'}
#action_idx = {'ceci':0, 'eric':1, 'hoon':2, 'jacky':3, 'mansion':4, 'peter':5, 'ryan':6, 'shuen':7, 'smallblue':8, 'wally':9, 'backpack':10, 'sidebag':11}
#reverse_ac_idx  = {0:'ceci', 1:'eric', 2:'hoon', 3:'jacky', 4:'mansion', 5:'peter', 6:'ryan', 7:'shuen', 8:'smallblue', 9:'wally', 10:'backpack', 11:'sidebag'}
#action_idx = {'ceci':0, 'eric':1, 'hoon':2, 'jacky':3, 'mansion':4, 'peter':5, 'ryan':6, 'shuen':7, 'smallblue':8, 'wally':9, 'backpack':10, 'sidebag':11, 'longtshirt':12, 'suit':13, 'coat':14}
#reverse_ac_idx  = {0:'ceci', 1:'eric', 2:'hoon', 3:'jacky', 4:'mansion', 5:'peter', 6:'ryan', 7:'shuen', 8:'smallblue', 9:'wally', 10:'backpack', 11:'sidebag', 12:'longtshirt', 13:'suit', 14:'coat'}
#action_idx = {'ceci':0, 'hoon':1, 'peter':2, 'shuen':3}
#reverse_ac_idx  = {0:'ceci', 1:'hoon', 2:'peter', 3:'shuen'}
#action_idx = {'tshirta':0, 'tshirtb':1, 'tshirtc':2, 'tshirtd':3}
#reverse_ac_idx  = {0:'tshirta', 1:'tshirtb', 2:'tshirtc', 3:'tshirtd'}
#action_idx = {'tshirta':0, 'longtshirt':1, 'suit':2, 'coat':3}
#reverse_ac_idx  = {0:'tshirta', 1:'longtshirt', 2:'suit', 3:'coat'}
#action_idx = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, 'i':8, 'j':9}
#reverse_ac_idx = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h', 8:'i', 9:'j'}
#action_idx     = {'no':0, 'backpack':1, 'sidebag':2}
#reverse_ac_idx = {0:'no', 1:'backpack', 2:'sidebag'}
#action_idx = {'tshirta':0, 'longtshirt':1, 'suit':2, 'coat':3, 'no':4, 'backpack':5, 'sidebag':6}
#reverse_ac_idx  = {0:'tshirta', 1:'longtshirt', 2:'suit', 3:'coat', 4:'no', 5:'backpack', 6:'sidebag'}

#action_idx     = {'run':0, 'walk':1}
#reverse_ac_idx = {0:'run', 1:'walk'}
#action_idx     = {'still':0, 'jump':1, 'pickbox':2, 'swing':3}
#reverse_ac_idx = {0:'still', 1:'jump', 2:'pickbox', 3:'swing'}
#action_idx     = {'click':0, 'slide':1, 'round':2, 'tune':3, 'empty':4}
#reverse_ac_idx = {0:'click', 1:'slide', 2:'round', 3:'tune', 4:'empty'}
#action_idx     = {'box':0, 'jog':1, 'run':2, 'walk':3, 'wave':4, 'clap':5, 'empty':6}
#reverse_ac_idx = {0:'box', 1:'jog', 2:'run', 3:'walk', 4:'wave', 5:'clap', 6:'empty'}
#action_idx     = {'box':0, 'kick':1, 'jump':2, 'squat':3, 'wave':4, 'clap':5, 'empty':6}
#reverse_ac_idx = {0:'box', 1:'kick', 2:'jump', 3:'squat', 4:'wave', 5:'clap', 6:'empty'}
#action_idx = {'a_empty': 0, 'b_empty': 1, 'c_empty': 2, 'd_empty': 3, 'e_empty': 4, 'f_empty': 5} 
#reverse_ac_idx = {0: 'a_empty', 1: 'b_empty', 2: 'c_empty', 3: 'd_empty', 4: 'e_empty', 5: 'f_empty'} 
#location_idx = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5}
#reverse_loc_idx = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f'}
#loc_ac_idx = {'a_clap': 0, 'a_box': 1, 'a_wave': 2, 'a_jump': 3, 'a_kick': 4, 'a_empty': 5, 'a_squat': 6, 'b_clap': 7, 'b_box': 8, 'b_wave': 9, 'b_jump': 10, 'b_kick': 11, 'b_empty': 12, 'b_squat': 13, 'c_clap': 14, 'c_box': 15, 'c_wave': 16, 'c_jump': 17, 'c_kick': 18, 'c_empty': 19, 'c_squat': 20, 'd_clap': 21, 'd_box': 22, 'd_wave': 23, 'd_jump': 24, 'd_kick': 25, 'd_empty': 26, 'd_squat': 27, 'e_clap': 28, 'e_box': 29, 'e_wave': 30, 'e_jump': 31, 'e_kick': 32, 'e_empty': 33, 'e_squat': 34, 'f_clap': 35, 'f_box': 36, 'f_wave': 37, 'f_jump': 38, 'f_kick': 39, 'f_empty': 40, 'f_squat': 41}
#reverse_loc_ac_idx = {0: 'a_clap', 1: 'a_box', 2: 'a_wave', 3: 'a_jump', 4: 'a_kick', 5: 'a_empty', 6: 'a_squat', 7: 'b_clap', 8: 'b_box', 9: 'b_wave', 10: 'b_jump', 11: 'b_kick', 12: 'b_empty', 13: 'b_squat', 14: 'c_clap', 15: 'c_box', 16: 'c_wave', 17: 'c_jump', 18: 'c_kick', 19: 'c_empty', 20: 'c_squat', 21: 'd_clap', 22: 'd_box', 23: 'd_wave', 24: 'd_jump', 25: 'd_kick', 26: 'd_empty', 27: 'd_squat', 28: 'e_clap', 29: 'e_box', 30: 'e_wave', 31: 'e_jump', 32: 'e_kick', 33: 'e_empty', 34: 'e_squat', 35: 'f_clap', 36: 'f_box', 37: 'f_wave', 38: 'f_jump', 39: 'f_kick', 40: 'f_empty', 41: 'f_squat'} 

def getModalFeature(featDir):
    actionFeat = {}
    print featDir
    for f in os.listdir(featDir):
        with open(os.path.join(featDir, f)) as inf:
            for line in inf:
                name, feat  = line.strip().split(' ', 1)
                feat, label = feat.strip().rsplit(' ', 1)

                feat = [float(val) for val in feat.split(' ')]

                if actionFeat.get(name, '') == '':
                    actionFeat[name] = {}
                    actionFeat[name]['feat'] = {}
                    actionFeat[name]['lbl'] = label

                actionFeat[name]['feat'][f] = feat

    cnt = 0
    for f in os.listdir(featDir):
        incomplete = []
        for key, val in actionFeat.iteritems():
            if val['feat'].get(f, "") == "":
                incomplete.append(key)
                cnt += 1
        for fail in incomplete:
            actionFeat.pop(fail, None);

    #print 'Deleted ' + str(cnt) + ' incomplete instances...'
    return actionFeat

def getProb(testSet, trainSet, fileList, items):
    probs = np.zeros((len(testSet), len(items)))
    #print len(trainSet)

    for f in fileList:
        trainData = []; trainLbl = []
        testData  = []; testLbl  = [] 
        for key, val in trainSet.iteritems():
            trainData.append(val['feat'][f])
            trainLbl.append(val['lbl'])
        for key, val in testSet.iteritems():
            testData.append(val['feat'][f])
            testLbl.append(val['lbl'])

        clf = svm.SVC(probability=True, kernel='linear')
        clf.fit(trainData, trainLbl)

        prob = clf.predict_proba(testData)
        probs += prob

    #for prob, lbl in zip(probs, testLbl):
        #print reverse_ac_idx[int(lbl)] + ' -> ' + reverse_ac_idx[int(np.argmax(prob))]
        #print reverse_loc_idx[int(lbl)] + ' -> ' + reverse_loc_idx[int(np.argmax(prob))]

    return probs / len(fileList)

def earlyFusion(testSet, trainSet, fileList, items):
    trainData = []; trainLbl = []
    testData  = []; 
    for key, val in trainSet.iteritems():
        concate_feat = [feat for f in fileList for feat in val['feat'][f]]
        trainData.append(concate_feat)
        trainLbl.append(val['lbl'])
    for key, val in testSet.iteritems():
        concate_feat = [feat for f in fileList for feat in val['feat'][f]]
        testData.append(concate_feat)

    clf = svm.SVC(probability=True, kernel='linear')
    clf.fit(trainData, trainLbl)

    prob = clf.predict_proba(testData)

    return prob / len(fileList)

def confusionMatrix(conf_arr, label, path='confusion_matrix.png'):
    norm_conf = []
    for i in conf_arr:
        a = 0
        tmp_arr = []
        a = sum(i, 0)
        for j in i:
            tmp_arr.append(float(j)/float(a))
        norm_conf.append(tmp_arr)
    
    fig = plt.figure(figsize=(10,10))
    plt.clf()
    plt.grid(True, color='white')
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    #res = ax.pcolor(np.array(norm_conf), cmap=plt.cm.jet, edgecolor='black', linestyle=':', lw=1)
    res = ax.imshow(np.array(norm_conf), cmap=plt.cm.jet, interpolation='nearest')
    
    width = len(conf_arr)
    height = len(conf_arr[0])
    
    #for x in xrange(width):
    #    for y in xrange(height):
    #        ax.annotate(str(conf_arr[x][y]), xy=(y, x), 
    #                    horizontalalignment='center',
    #                    verticalalignment='center')
    
    cb = fig.colorbar(res)

    #alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    plt.xticks(range(width), label[:width], rotation=90)
    plt.yticks(range(height), label[:height])
    plt.savefig(path, format='png')

def consClassifiers(trainSet, fileList, locations):
    classifiers = {key: {f:None for f in fileList} for key in locations}

    for loc in locations:
        lbl_no = location_idx[loc]
        for f in fileList:
            trainData = []; trainLbl = []
            for key, val in trainSet.iteritems():
                if val['loc'] != lbl_no:
                    continue
                trainData.append(val['feat'][f])
                trainLbl.append(val['lbl'])

            clf = svm.SVC(probability=True, kernel='linear')
            clf.fit(trainData, trainLbl)
            classifiers[loc][f] = clf
    return classifiers

def predictAction(classifier, testData, fileList):
    probs = np.zeros((1, len(action_idx)))
    for f in fileList:
        prob = classifier[f].predict_proba(testData['feat'][f])
        probs += prob
    
    return probs
