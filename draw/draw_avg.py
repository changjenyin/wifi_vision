import os
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Agg')

from scipy import signal
from matplotlib import pyplot as plt
from math import log10

action_idx = {'box':1, 'jump':2, 'wave':3, 'clap':4, 'kick':5, 'squat':6, 'empty':7}

SAMPLING_RATE = 1000
def butter_lowpass(cutoff, fs=SAMPLING_RATE, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def main():
    if len(sys.argv) != 3:
        print 'Usage: draw_pow.py in_dir out_dir'

    in_dir  = sys.argv[1]
    out_dir = sys.argv[2]
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    cate_avg = {action: np.zeros((4, 4500)) for action in action_idx.keys()}
    cate_cnt = {action: 0 for action in action_idx.keys()}
    for action in os.listdir(in_dir):
        cate = ''.join([i for i in action if not i.isdigit()])
        cate_cnt[cate] += 1

        path = os.path.join(in_dir, action, 'avg')

        feats = []
        plt.figure()
        with open(path, 'r') as inf:
            vmin = 1000
            vmax = -1000
            for idx, line in enumerate(inf):
                a = max([float(val) for val in line.strip().split(' ')])
                feat = [10*log10(float(val)) for val in line.strip().split(' ')]


                b, a = butter_lowpass(10)
                filtered_dat = signal.lfilter(b, a, feat)

                if len(feat) >= 4500:
                    cate_avg[cate][idx] += np.asarray(filtered_dat)[0:4500]

                feats.append(filtered_dat)

                if max(feat) > vmax:
                    vmax = max(feat)
                if min(feat) < vmin:
                    vmin = min(feat)

        for feat in feats:
            plt.plot(feat)

        plt.savefig(os.path.join(out_dir, action + '.jpg'))
        plt.close()

    for action, feat in cate_avg.iteritems():
        plt.figure()
        for row in cate_avg[action]:
            dat = row / cate_cnt[cate]
            plt.plot(dat)

        plt.savefig(os.path.join(out_dir, action + '_avg.jpg'))
        plt.close()

if __name__ == '__main__':
    main()
