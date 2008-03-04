from createFlare import randomFlare, writeXml, runObsSim
from find_flare_2 import find_flare, first_rise

#import hippoplotter as plot
#
#nt = plot.newNTuple(([], [], []), ('true start', 'est. 1', 'est. 2')
#plot.Scatter(nt, 'true start', 'est. 1')
#plot.Scatter(nt, 'true start', 'est. 2')

file = open('trade_study_1.dat', 'w')

ntrials = 500
for i in xrange(ntrials):
    src, tstart = randomFlare(flux=0.1, window=(0, 2*8.64e4))
    xmlFile = 'random_flare.xml'
    writeXml(src, xmlFile)
    runObsSim(xmlFile, 'random_flare')
    (evts, flare_evts, flare_blocks,
     flare_blocks_ea) = find_flare('random_flare_events_0000.fits',
                                   'eg_diffuse_events_0000.fits')
    onset = first_rise(flare_blocks)
    ea_onset = first_rise(flare_blocks_ea)

    file.write(('%.2e '*3 % (tstart, onset, ea_onset)) + '\n')
    
#    nt.addRow((onset/tstart, ea_onset/tstart))
