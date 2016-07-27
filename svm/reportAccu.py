import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from sklearn import svm

def main():
    combinePy = '/tmp4/transfer/WiSee/new_intel_csi/signal_process/feature/combineDir.py'
    featDir   = '/tmp4/transfer/WiSee/new_intel_csi/signal_process/feature/MM2016/'
    abRoot    = '/tmp4/transfer/WiSee/new_intel_csi/signal_process/feature/abTesting/gabor'
    methods   = ['120svd_1', '120svd_4', '30svd_1', '30svd_4']
    #names     = ['power_20160129_R540', 'power_20160131_R544', 'power_20160129_R544_bf', 'power_20160129_R544_fb', 'power_20160203_R542', 'power_20160204_R542_bf', 'power_20160301_R546_middle', 'power_20160304_R539', 'power_20160304_R546']
    #names     = ['20160129_R540', '20160131_R544', '20160129_R544_bf', '20160129_R544_fb', '20160203_R542', '20160204_R542_bf', '20160301_R546_middle', '20160304_R539', '20160304_R546']
    names     = ['R539', 'R540', 'R542', 'R544', 'R546'] 

    config = sys.argv[1]
    report = sys.argv[2]

    if config == '1v1':
        create1v1ConfigFile(names)
        config = 'configs/1v1.config'
    elif config == 'all_cross':
        createCrossValAllRoomConfigFile(names)
        config = 'configs/all_cross.config'
    print 'Reading config file...'

    accus = []
    with open(report, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')

        with open(config, 'U') as inf:
            for line in inf:
                if line.strip() == '':
                    continue

                # Testing two SVD denoise ways  
                results = []
                for setup in ['MIMO', 'SISO']:
                    featRoot = os.path.join(featDir, setup) 
                #for setup in ['MIMO']:
                #    featRoot = featDir

                    modal   = os.path.basename(abRoot)
                    abTrain = os.path.join(abRoot, 'train', modal)
                    abTest  = os.path.join(abRoot, 'test', modal)

                    parts    = line.strip().split(' ')
                    trainIdx = parts.index('train')
                    testIdx  = parts.index('test')
                    trainDir = parts[trainIdx+1:testIdx] 
                    testDir  = parts[testIdx+1:]

                    ## Combine features from multiple directories
                    # Training data
                    if len(trainDir) > 1:
                        combineCmd = 'python ' + combinePy
                        for folder in trainDir:
                            path = os.path.join(featRoot, folder)
                            combineCmd = combineCmd + ' ' + path

                        print 'Combining training directories...'
                        finalTrain = os.popen(combineCmd).read().strip()
                    else: 
                        finalTrain = os.path.join(featRoot, trainDir[0])

                    # Testing Data
                    if len(testDir) > 1:
                        combineCmd = 'python ' + combinePy
                        for folder in testDir:
                            path = os.path.join(featRoot, folder)
                            combineCmd = combineCmd + ' ' + path

                        print 'Combining testing directories...'
                        finalTest = os.popen(combineCmd).read().strip()
                    else:
                        finalTest = os.path.join(featRoot, testDir[0])
                    
                    # Single classifier abTesting 
                    print 'Training single_classfier...'
                    abTestingCmd = 'python single_classifier_abTesting.py 1 ' + finalTrain + ' ' + finalTest
                    result = os.popen(abTestingCmd).read()
                    results.append(result.strip().split('\n')[-1])

                    # 4 classifier abTesting
                    cpTrainCmd = 'cp ' + finalTrain + '/* '  + abTrain
                    cpTestCmd  = 'cp ' + finalTest  + '/* '  + abTest
                    os.system(cpTrainCmd)
                    os.system(cpTestCmd)

                    print 'Training classfiers...'
                    abTestingCmd = 'python abTesting.py 1 ' + abRoot
                    result = os.popen(abTestingCmd).read()
                    results.append(result.strip().split('\n')[-1])
            
                accus.append(results)

                print 'Training: ' + os.path.basename(finalTrain)
                print 'Testing: '  + os.path.basename(finalTest)
                print '\n'
                results = [os.path.basename(finalTrain), os.path.basename(finalTest)] + results
                writer.writerow(results)
       
        if config == 'configs/1v1.config':
            confusionTable(accus, names, methods)

def createCrossValAllRoomConfigFile(names):
    with open('configs/all_cross.config', 'w') as outf:
        for name1 in names:
            outf.write('train')
            for name2 in names:
                if name2 == name1:
                    continue
                outf.write(' ' + name2)
            outf.write(' test ' + name1 + '\n')

def create1v1ConfigFile(names):
    with open('configs/1v1.config', 'w') as outf:
        for name1 in names:
            for name2 in names:
                outf.write('train ' + name1 + ' test ' + name2 + '\n')

def confusionTable(accus, names, methods):
    conf_arr = np.asarray(accus, dtype=np.float32)
    numDir = len(names)
    numMethod = len(accus[0])

    for j in range(numMethod):
        confusionMatrix(conf_arr[:,j].reshape(numDir, numDir), names, 'confusion_' + methods[j] + '.jpg')

def confusionMatrix(conf_arr, label, path='confusion_matrix.png'):
    norm_conf = []
    for i in conf_arr:
        tmp_arr = []
        for j in i:
            tmp_arr.append(float(j))
        norm_conf.append(tmp_arr)
    
    fig = plt.figure(figsize=(10,10))
    plt.clf()
    plt.grid(True, color='white')
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    res = ax.imshow(np.array(norm_conf), cmap=plt.cm.jet, interpolation='nearest')
    
    width = len(conf_arr)
    height = len(conf_arr[0])
    
    for x in xrange(width):
        for y in xrange(height):
            ax.annotate(str(conf_arr[x][y]), xy=(y, x), 
                        horizontalalignment='center',
                        verticalalignment='center')
    
    cb = fig.colorbar(res)
    plt.xticks(range(width), label[:width], rotation=90)
    plt.yticks(range(height), label[:height])
    plt.savefig(path, format='png')

if __name__ == '__main__':
    main()
