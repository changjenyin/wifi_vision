import os
import sys
from multiprocessing import Pool
from functools import partial

imgWidth    = "576";
imgHeight   = "432";
gaborExeDir = '/tmp4/transfer/WiSee/new_intel_csi/signal_process/gabor'

def parseSet(rawFeatDir, parsedDir, power, folder):
    # Parse csi 
    rawPath     = os.path.join(rawFeatDir, folder)
    parsedPath  = os.path.join(parsedDir, folder)
    parseCmd    = "matlab -r \"parse_csi_whole('" + rawPath + "', '" + parsedPath + "', " + power + "), exit\""
    os.system(parseCmd)

def denoiseSet(parsedDir, denoise, imgDir, folder):
    # Apply denoising
    parsedPath  = os.path.join(parsedDir, folder)
    imgPath     = os.path.join(imgDir, folder)
    denoiseCmd  = "matlab -r \"" + denoise + "('" + parsedPath + "', '" + imgPath + "', " + imgWidth + ", " + imgHeight + "), exit\""
    os.system(denoiseCmd)

def extractFeat(imgDir, gaborDir, folder):
    # Extract Gabor feature 
    os.chdir(gaborExeDir)

    #imgPath     = os.path.join(imgDir, folder)
    imgPath     = os.path.join(imgDir)
    #gaborPath   = os.path.join(gaborDir, folder)
    gaborPath   = os.path.join(gaborDir)
    gaborCmd    = "python id_gabor.py " + imgPath + " " + gaborPath + " 8 6 0"
    os.system(gaborCmd)

def main():
    if len(sys.argv) != 7:
        print 'python automate.py rawFeatDir parsedDir power method imgDir gaborDir'
        exit()

    cwd = os.path.dirname(os.path.realpath(__file__))

    rawFeatDir  = sys.argv[1]
    parsedDir   = sys.argv[2]
    power       = sys.argv[3]
    denoise     = sys.argv[4]
    imgDir      = sys.argv[5]
    gaborDir    = sys.argv[6]

    if denoise != 'low_avg' and denoise != 'svd4H' and denoise != 'svd4H_1v1' and denoise != 'none':
        print 'Denoising method should be one of the following: low_avg, svd4H, svd4H_1v1, none...'
        exit()

    # Consistency check between imgDir and denoise method
    if denoise == 'svd4H' and imgDir.find('MIMO') == -1:
        print 'svd4H should output to MIMO img directory...'
        exit()
    if denoise == 'svd4H_1v1' and imgDir.find('SISO') == -1:
        print 'svd4H_1v1 should output to SISO img directory...'
        exit()

    # Parallel processing each dataset
    pool = Pool()

    func = partial(parseSet, rawFeatDir, parsedDir, power)
    pool.map(func, os.listdir(rawFeatDir))
    func = partial(denoiseSet, parsedDir, denoise, imgDir)
    pool.map(func, os.listdir(rawFeatDir))

    func = partial(extractFeat, imgDir, gaborDir)
    pool.map(func, os.listdir(rawFeatDir))

    pool.close()
    pool.join()


if __name__ == '__main__': 
    main()
