import os
import sys
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from scipy import signal
SUB_CNT = 30
SAMPLING_RATE = 1000

def butter_lowpass(cutoff, fs=SAMPLING_RATE, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def main():
    if len(sys.argv) != 3:
        print 'Usage: python vis_stream.py input_dir output_dir'
        exit()
    
    in_dir  = sys.argv[1]
    out_dir = sys.argv[2]
    
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    for action in os.listdir(in_dir):
        fig_dir = os.path.join(out_dir, 'avg')
        if not os.path.isdir(fig_dir):
            os.mkdir(fig_dir)
        with open(os.path.join(in_dir, action, 'avg'), 'r') as inf:
            fig = plt.figure()
            cnt = 1
            for line in inf:
                plt.subplot(4, 1, cnt)
                plt.plot([float(val) for val in line.strip().split(' ')])
                cnt += 1
            plt.savefig(os.path.join(fig_dir, action), bbox_inches='tight')
            plt.close()
    
    cnt = 0
    fileList = ['1.ant', '2.ant', '3.ant', '4.ant']
    for f in fileList:
        fps = {action: open(os.path.join(in_dir, action, f), 'r') for action in os.listdir(in_dir)}
    
        for i in range(SUB_CNT):
            fig_dir = os.path.join(out_dir, str(cnt))

            print fig_dir
            if not os.path.isdir(fig_dir):
                os.mkdir(fig_dir)
    
            for name, fp in fps.iteritems():
                dat = [float(val) for val in fp.readline().strip().split(' ')]
    
                b, a = butter_lowpass(10)
                filtered_dat = signal.lfilter(b, a, dat)
    
                fig = plt.figure()
                plt.plot(filtered_dat)  
                
                path = os.path.join(fig_dir, name)
                plt.savefig(path, bbox_inches='tight')
                plt.close()
    
            cnt += 1
        for fp in fps.itervalues():
            fp.close()

if __name__ == '__main__':
    main()
