class GrbSrcIds(dict):
    def __init__(self, infile='/nfs/farm/g/glast/u33/jchiang/ASP/GRB/GRBS_MC_SRC_ID.dat'):
        for line in open(infile):
            tokens = line.split()
            self[tokens[0]] = tokens[1]

if __name__ == '__main__':
    grbSrcIds = GrbSrcIds()
    for item in grbSrcIds:
        print item, grbSrcIds[item]
