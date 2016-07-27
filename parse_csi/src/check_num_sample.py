with open('../result/csi.bin', 'U') as inf:
    for line in inf:
        feats = line.strip().split(' ')
        print len(feats)
        break
