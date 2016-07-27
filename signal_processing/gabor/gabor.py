# python gabor.py [input_dir] [output_dir] [#orientation] [#scale] [doEqual]
import os
import sys
import re
import numpy as np
import cv2
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
sys.path.append('../lib')
from readMatToImg import readMatToImg

ANT_PAIR = 4
#action_idx  = {'box':0, 'clap':1, 'empty':2, 'jog':3, 'run':4, 'walk':5, 'wave':6}
#action_idx = {'box':0, 'jog':1, 'run':2, 'walk':3, 'wave':4, 'clap':5, 'empty':6}
#action_idx  = {'box':0, 'kick':1, 'jump':2, 'squat':3, 'wave':4, 'clap':5, 'empty':6}
#action_idx  = {'click':0, 'slide':1, 'round':2, 'tune':3, 'empty':4}
#action_idx = {'boxing':0, 'jump':1, 'pickbox':2, 'run':3, 'swing':4, 'walk':5}
action_idx = {'still':0, 'jump':1, 'pickbox':2, 'run':3, 'swing':4, 'walk':5}
#action_idx = {'still':0, 'run':1, 'walk':2}
#action_idx = {'a_clap': 0, 'a_box': 1, 'a_wave': 2, 'a_jump': 3, 'a_kick': 4, 'a_empty': 5, 'a_squat': 6, 'b_clap': 7, 'b_box': 8, 'b_wave': 9, 'b_jump': 10, 'b_kick': 11, 'b_empty': 12, 'b_squat': 13, 'c_clap': 14, 'c_box': 15, 'c_wave': 16, 'c_jump': 17, 'c_kick': 18, 'c_empty': 19, 'c_squat': 20, 'd_clap': 21, 'd_box': 22, 'd_wave': 23, 'd_jump': 24, 'd_kick': 25, 'd_empty': 26, 'd_squat': 27, 'e_clap': 28, 'e_box': 29, 'e_wave': 30, 'e_jump': 31, 'e_kick': 32, 'e_empty': 33, 'e_squat': 34, 'f_clap': 35, 'f_box': 36, 'f_wave': 37, 'f_jump': 38, 'f_kick': 39, 'f_empty': 40, 'f_squat': 41}
#action_idx  = {'a_empty': 0, 'b_empty': 1, 'c_empty': 2, 'd_empty': 3, 'e_empty': 4, 'f_empty': 5}
#action_idx = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5}
#action_idx = {'ceci':0, 'eric':1, 'hoon':2, 'jacky':3, 'mansion':4, 'peter':5, 'ryan':6, 'shuen':7, 'smallblue':8, 'wally':9}
#action_idx = {'ceci':0, 'eric':1, 'hoon':2, 'jacky':3, 'mansion':4, 'peter':5, 'ryan':6, 'shuen':7, 'smallblue':8, 'wally':9, 'backpack':10, 'sidebag':11, 'longtshirt':12, 'suit':13, 'coat':14}
#action_idx = {'ryan':6}
#action_idx = {'tshirta':0, 'tshirtb':1, 'tshirtc':2, 'tshirtd':3}
#action_idx = {'tshirta':0, 'longtshirt':1, 'suit':2, 'coat':3}
#action_idx = {'ceci':0, 'hoon':1, 'peter':2, 'shuen':3}
#action_idx = {'no':0, 'backpack':1, 'sidebag':2}
#action_idx = {'tshirta':0, 'longtshirt':1, 'suit':2, 'coat':3, 'no':4, 'backpack':5, 'sidebag':6}

def image_histogram_equalization(image, number_bins=256):
    # from http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html

    # get image histogram
    image_histogram, bins = np.histogram(image.flatten(), number_bins, normed=True)
    cdf = image_histogram.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize

    # use linear interpolation of cdf to find new pixel values
    image_equalized = np.interp(image.flatten(), bins[:-1], cdf)

    return image_equalized.reshape(image.shape), cdf

def build_filters(num_scale, num_orien):
    filters = []
    ksize = 15
    gamma = 1
    scale_step = 2.1/num_scale  # 3.1 - 1 = 2.0
    for theta in np.arange(0, np.pi, np.pi / num_orien):
        for sigma in np.arange(1, 3.1, scale_step):
            lamda = sigma + 1
            #print 'ksize = ', ksize, ', gamma = ', gamma, 'theta = ', theta, 'sigma = ', sigma, 'lambda = ', lamda
            kern = cv2.getGaborKernel((ksize, ksize), sigma, theta, lamda, gamma, 0, ktype=cv2.CV_32F)
            kern /= 1.5 * kern.sum()
            filters.append(kern)

    # Append more vertical filters
    #vksize = 17
    #vtheta = 0
    #for sigma in np.arange(1, 3.1, 0.4):
    #    lamda = sigma + 1
    #    kern = cv2.getGaborKernel((vksize, vksize), sigma, vtheta, lamda, gamma, 0, ktype=cv2.CV_32F)
    #    kern /= 1.5 * kern.sum()
    #    filters.append(kern)

    return filters

def process(img, one_filter):
    accum = np.zeros_like(img)
    fimg = cv2.filter2D(img, -1, one_filter)
    #accum = np.maximum(accum, fimg)
    np.maximum(accum, fimg, accum)

    return accum

def main():
    # Read in 4_jpg/ (each directory corresponding to a training data)
    if len(sys.argv) != 6:
        print 'Usage: python gabor.py input_dir output_dir num_orien num_scale doHistEq'

    input_dir  = sys.argv[1]
    basename = input_dir.split('/')
    if basename[-1] == '':
        basename = basename[-2]
    else:
        basename = basename[-1]

    #if not os.path.isdir(os.path.join('filtered_map', basename)):
    #    os.mkdir(os.path.join('filtered_map', basename))

    output_dir = sys.argv[2]
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    num_orien  = int(sys.argv[3])
    num_scale  = int(sys.argv[4])
    doHistEqual= int(sys.argv[5])

    output_file_list = []
    for i in xrange(0, ANT_PAIR):
        outf = open(output_dir + '/' + str(i + 1) + '_feat', 'w')
        output_file_list.append(outf)
    
    # Read in every channel for each training data
    # EX: directory = 'jog8', image_file = '3.jpg'
    dir_list = os.listdir(input_dir)
    for directory in dir_list:
        # Do not process folder of original CSIs
        if directory == 'orig':
            continue

        # Create image directory if not exists
        #img_dir = os.path.join('filtered_map', basename, directory)
        #if not os.path.isdir(img_dir):
        #    os.mkdir(img_dir)

        # Remove empty
        #cate = re.search('([a-z]+)\d+', directory).group(1)
        #if cate == 'empty': continue
    
        print 'Processing ' + directory + ' ...'
        file_list = os.listdir(input_dir + '/' + directory)
        
        # Get gabor filters
        filters = []
        filters = build_filters(num_scale, num_orien)
        filters = np.asarray(filters)
           
        #fig = plt.figure()
        '''
        for i in xrange(0, len(filters)):
            ax = fig.add_subplot(1, len(filters), i)
            plt.imshow(filters[i], cmap=mpl.cm.gray)
        '''
        '''
        for i in xrange(0, len(filters)):
            plt.imshow(filters[i], cmap=mpl.cm.gray)
            plt.savefig("filters_svg/filter" + str(i) + ".svg", format="svg")
        print 'svg finish'
        raw_input()
        '''

        #numChannel = len(file_list)
        #step = 1.0/numChannel
        for idx, image_file in enumerate(file_list):
            if os.path.splitext(image_file)[0] == 'room':
                continue
            feature = []
    
            # Read in img and convert to gray-scale
            img = cv2.imread(input_dir + '/' + directory + '/' + image_file)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Decide if need histequal
            if doHistEqual:
                img = cv2.equalizeHist(img)
            #if not os.path.isdir(output_dir + '/' + directory):
            #    os.mkdir(output_dir + '/' + directory)
            #cv2.imwrite(output_dir + '/' + directory + '/' + image_file, img)
         
            # Apply filters on img
            res = []
            for i in xrange(len(filters)):
                res1 = process(img, filters[i])
                res.append(np.asarray(res1))
            ''' 
            #fig.subplots_adjust(left=0, bottom=1-(idx+1)*step, right=1, top=1-idx*step, hspace=0)
            #ax = fig.add_subplot(numChannel, 1, idx+1)
            ax = fig.add_axes([0, 1-(idx+1)*step, 1, step])

            ax.axis('off')
            ax.axes.get_xaxis().set_visible(False)
            ax.axes.get_yaxis().set_visible(False)

            plt.imshow(res[0], cmap=mpl.cm.gray, aspect='auto')

            plt.savefig(os.path.join(img_dir, 'res.jpg'), pad_inches=0)
            plt.close()
            '''
            '''
            fig = plt.figure()
            ax = fig.add_subplot(1, 3, 1)
            plt.imshow(img, cmap=mpl.cm.gray)
            ax = fig.add_subplot(1, 3, 2)
            plt.imshow(filters[8], cmap=mpl.cm.gray)
            ax = fig.add_subplot(1, 3, 3)
            plt.imshow(res[8], cmap=mpl.cm.gray)
            plt.show()
            '''
            # Calculate mean, std for each filtered result
            for i in xrange(len(res)):
                mean = np.mean(res[i])
                std = np.std(res[i])
                feature.append(mean)
                feature.append(std)
            
            # Get ant_pair_index for i_feat
            ant_pair_index, ext = os.path.splitext(image_file)
            ant_pair_index = int(ant_pair_index) - 1
            # Write data name
            output_file_list[ant_pair_index].write('%s ' % directory)

            # Write features of each channel
            #feature[0:len(feature):2] = feature[0:len(feature):2] / sum(feature[0:len(feature):2])
            for f in feature:
                output_file_list[ant_pair_index].write('%s ' % f)

            # Write label
            label = re.search('([\D]+)\d+', directory).group(1)
            label = action_idx.get(label, '-1')
            if label == '-1':
                continue
            output_file_list[ant_pair_index].write('%s\n' % label)

if __name__ == '__main__':
    main()
