from pksData import *

hist = plot.Histogram(diffuse[0], 'TIME')
plot.Histogram(galdiffuse[0], 'TIME', oplot=1, color='blue')
plot.Histogram(pks1622[0], 'TIME', oplot=1, color='red')
reps = hist.getDataReps()
#reps[0].setErrorDisplay('y', 1)

hist.setRange('x', 1233345., 1778969.)

my_cuts = (plot.hippo.Cut(diffuse[0], ('distance', )),
           plot.hippo.Cut(galdiffuse[0], ('distance', )), 
           plot.hippo.Cut(pks1622[0], ('distance', )))

for cut, rep in zip(my_cuts, reps):
    rep.applyCut(cut)
    cut.setCutRange(0, 20, 'distance')

nt1 = reps[0].createNTuple()
nt2 = reps[1].createNTuple()
nt3 = reps[2].createNTuple()

plot.canvas.removeDisplay(hist)

hist = plot.Scatter(nt1, 'X', 'Value', pointRep='Column', yrange=(0, 0.09))
diffuse_rep = hist.getDataRep()
gd_rep = plot.Scatter(nt2, 'X', 'Value', pointRep='Column', oplot=1,
                      color='blue')
flare_rep = plot.Scatter(nt3, 'X', 'Value', pointRep='Column', oplot=1,
                         color='red')

gd_rep.setBinWidth('x', 1000.)

hist.setLabel('x', 'Time (s)')
hist.setLabel('y', 'Counts/s')

#sys.path.append('../python')
#from BayesBlocks import BayesBlocks, LightCurve
#
#def get_BB_lightCurve(nt, cut):
#    rep = plot.hippo.DataRep('Y Plot', nt, ('TIME',))
#    rep.applyCut(cut)
#    tt = rep.getNTupleWithCuts().getColumn('TIME')
#    blocks = BayesBlocks(tt)
#    xx, yy = LightCurve(blocks.computeLightCurve()).dataPoints()
#    return xx, yy, tt, blocks
#
#(tt_diffuse, flux_diffuse,
# diffuse_times, diffuse_blocks) = get_BB_lightCurve(diffuse[0], my_cuts[0])
#                                                    
#(tt_flare, flux_flare,
# flare_times, flare_blocks) = get_BB_lightCurve(pks1622[0], my_cuts[1])
#
#plot.scatter(tt_flare, flux_flare, 'Time (s)', 'Counts/s',
#             pointRep='Line', color='red', ylog=1)
#plot.scatter(tt_diffuse, flux_diffuse, pointRep='Line', oplot=1)
#
#combined = list(diffuse_times) + list(flare_times)
#combined.sort()
#combined_blocks = BayesBlocks(combined, 8)
#
#diffuse_lc = LightCurve(diffuse_blocks.computeLightCurve())
#scaleFactors = diffuse_lc(combined)
#combined_blocks.setCellScaling(scaleFactors)
#
#flare_lc = LightCurve(combined_blocks.computeLightCurve())
#(tt, ff) = flare_lc.dataPoints()
#
#plot.scatter(tt, ff, 'Time (s)', 'Counts/s', pointRep='Line')
#
#from read_data import read_data
#import os
#template = read_data(os.path.join(os.environ['OBSERVATIONSIMROOT'],
#                                  'data/pks1622-297_Template.dat'))
#plot.scatter(template[0], template[1]/max(template[1])*0.4, pointRep='Line',
#             lineStyle='Dot', oplot=1)
