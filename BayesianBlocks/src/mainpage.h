/**
   @page Results Using Bayesian Blocks to Find Spectral Features and AGN Flares in LAT Data

   @section intro Introduction
                  
   As part of an effort to understand it, but also to see if it could
   be used to detect day time scale transients in LAT data, I
   implemented Jeff Scargle's Bayesian Blocks algorithm for 1D data.
   The main reference that I used is the article by <a
   href="http://trotsky.arc.nasa.gov/~jeffrey/paper_1d.pdf">Jackson,
   Scargle, et al. 2003</a>.  I also consulted Jeff's longer <a
   href="http://trotsky.arc.nasa.gov/~jeffrey/global.ps">Paper VI</a>
   for more details and the MatLab implementation, and Mike Nowak's <a
   href="http://space.mit.edu/CXC/analysis/SITAR/bb_examp.html">SITAR
   pages</a> for his <a href="http://www.s-lang.org/">S-Lang</a>/<a
   href="http://space.mit.edu/CXC/ISIS/">ISIS</a> version.  I won't
   describe the underlying algorithm in its entirety here, since it is
   well explained in the above references.  However, I am using it in
   a context that differs in an important way from the usual
   applications, so some details will need to be covered.

   The basic method is intended to find the optimal partition of the
   interval such that the data in the interval can be described by a
   "piece-wise constant function", i.e., that the density of events in
   the interval can be modeled as a series of step functions.  For 1D
   Bayesian Blocks, each photon event is characterized by a single
   quantity, such as arrival time or measured energy.  For arrival
   times, the method gives an estimate of the light curve while for
   energies, it gives an estimate of the spectrum.  

   Here are some definitions that will be useful for the following
   discussion:
      
   - The initial partitioning of the interval places each event in
     its own cell.  The boundaries of the cells are given by the
     mid-points between adjacent events.

   - A block is defined as a contiguous group of cells.

   - The content, \f$N\f$, of a block is the number of cells or events
     that it comprises.

   - The size, \f$M\f$, of a block is the sum of its individual cell
     sizes.

   - The ends of each block are referred to as change points, since
     they are the locations at which the rate changes from one
     constant value to another.

   - The cost function for each block is 
     \f[
     \log\Gamma(N + 1) + \log\Gamma(M - N + 1) - \log\Gamma(M + 2) 
         - \log\gamma,
     \f]
     where \f$\Gamma\f$ is the usual gamma-function, \f$\Gamma(x+1) =
     x\Gamma(x)\f$, and the total cost function of the partition is
     the sum of the individual block cost functions.  The above
     expression is based on a Poisson model for the expected number of
     counts in a block given a constant rate.  The last term,
     \f$\log\gamma\f$, describes a prior distribution that prefers a
     smaller number of change points.  Since larger values of
     \f$\log\gamma\f$ tend to produce less structured models, the
     value of \f$\log\gamma\f$ at which a given feature is suppressed
     can be considered as a measure of the "significance" of that
     feature.

   Here is an example of a Bayesian Blocks (hereafter BB) analysis:

   @image html BB_example_0.png

   For this plot, 200 events were drawn from the differential
   distribution
   
   \f[\frac{dN}{dx} \begin{array}[t]{l}
                      = 0.5 \qquad x < 0.5\\ \\
                      = 1   \qquad 0.5 \le x < 0.7\\ \\
                      = 0.5 \qquad 0.7 \le x < 1
                    \end{array}
   \f]

   The black histogram are these data binned into 50 equal-sized bins
   in \f$x\f$, and the red histogram is the BB estimate of the
   underlying distribution.  The dotted vertical lines indicate \f$x =
   0.5,\,0.7\f$, the "true" locations of the change points in the
   underlying distribution.

   @section photon_spectra Application to Photon Spectra 

   While the basic BB method can be applied to any sort of event data,
   it is most effective when the distribution in the null hypothesis
   is constant and the method is used to find deviations (or "flares")
   from a flat distribution.  If the intrinsic distribution of the
   events is itself highly structured then the method may not pick out
   discrete features that are still obvious to the eye.

   Here is a sampling of 1000 events following a power-law distribution,
   \f$dn/dE = E^{-2}\f$ along with 100 events from a Gaussian line with
   width 30 at energy \f$E_{\rm line} = 200\f$:

   @image html powerlaw_not_scaled.png

   As before, the black histogram is the data binned in equal-spaced
   (log-scale) bins and the red histogram is the BB estimate.  The
   dotted vertical line indicates the central energy of the line at
   200.  Although it is clear that the partition found by the BB
   algorithm has adjusted itself to account for the line component,
   the line feature is not very evident when considering the red
   histogram by itself.

   If one is looking for deviations from a known underlying
   distribution then the data can be "detrended" using that
   distribution by applying a scale factor, which is proportional to
   the underlying differential distribution, to each cell size.  For
   the power-law spectrum case we are considering, this means

   \f[
   M \begin{array}[t]{l} 
     \rightarrow M \times \frac{dn}{dE}\\ \\
     \rightarrow M E^{-2}
     \end{array}
   \f]

   For a pure power-law, the detrended data will follow a uniform
   distribution and any deviations from the power-law will be more
   prominent.  Here is a plot of the above data detrended:

   @image html powerlaw_detrended.png
   
   and the original data along with the BB estimate of those data
   "retrended" using the assumed \f$dn/dE\f$:

   @image html powerlaw_scaled.png

   Note that this procedure of detrending the data by scaling the cell
   sizes by the expected distribution is closely related to the
   application of the BB method Mike Nowak describes for <a
   href="http://space.mit.edu/CXC/analysis/SITAR/bb_experiment.html">finding
   residuals in spectral gratings data</a>.  In Mike's final
   expression for the marginalized likelihood of a block, the
   denominator is essentially the total model count rate for the
   assumed underlying distribution.  This factor plays the same role
   as the third term in our block cost function, \f$-\log\Gamma(M +
   2)\f$, since multiplying the cell size by \f$dn/dE\f$ means that
   the resulting block size \f$M\f$ is an estimate of the expected
   number of counts in that block.

   @section LAT_light_curves Detecting AGN Flares in LAT Data

   The main difficulty in detecting flaring sources in LAT data is
   that the exposure to any given location on the sky will be strongly
   modulated on orbital (95 minutes), diurnal (1 day), and
   precessional (55 days) timescales.  Furthormore, since the Galactic
   and extragalactic diffuse components will be the dominant
   contributions to the total LAT count rate at almost all time scales
   (except for GRB events), the contribution from even the brightest
   AGN flares seen by EGRET will be swamped by the Poisson
   fluctuations of the diffuse components if the total LAT count rates
   are considered:
   
   @image html pks1622_flare.png

   This is a plot of the expected LAT events due to the Galactic and
   extragalactic diffuse emission measured by EGRET, histogrammed as a
   function of time (black) for energies \f$E > 20 MeV\f$. Also
   plotted are the expected events from the bright flare seen by EGRET
   from the blazar PKS 1622-297 (red).  Even though this flare was
   unusually bright, its light curve is still comparable in magnitude
   to the Poission fluctuations of the diffuse components as shown
   by the error bars.

   One can increase the signal-to-noise in the flare emission versus
   the diffuse by considering events from smaller portions of the sky,
   but in this case the orbital and diurnal modulations are magnified:

   @image html pks1622_flare_20deg.png
   
   For these data, a 20 degree acceptance cone centered 

*/

//    For this plot, 5000 events were drawn from the differential
//    distribution
//    \f[
//    \frac{dn}{d\phi}\mbox{~}{\stackrel{d}{\sim}}\mbox{~}1 + \sin\phi.
//    \f]

