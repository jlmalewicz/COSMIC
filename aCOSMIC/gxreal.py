# -*- coding: utf-8 -*-
# Copyright (C) Scott Coughlin (2017)
#
# This file is part of aCOSMIC.
#
# aCOSMIC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aCOSMIC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with aCOSMIC.  If not, see <http://www.gnu.org/licenses/>.

"""`gxreal`
"""

import numpy as np
from gwpy.utils import mp as mp_utils
import pandas as pd
import aCOSMIC.MC_samp as MC_samp


__author__ = 'Katelyn Breivik <katie.breivik@gmail.com>'
__credits__ = 'Scott Coughlin <scott.coughlin@ligo.org>'
__all__ = ['GxReal']

class GxReal(object):
    def __init__(self, fixed_pop, m_tot_samp, gx_model, gx_component, dat_list):
        '''
        Initialize GxReal
        '''
        self.fixed_pop = fixed_pop
        self.fixed_mass = m_tot_samp
        self.gx_model = gx_model
        self.gx_component = gx_component
        self.dat_list = dat_list 

        return


    def compute_n_sample(self):
        """Use the fixed population and total mass sampled to generate the 
        fixed population to compute the number of systems in the Milky Way
        realization

        Parameters
        ----------
        fixedpop (DataFrame):
            Contains binary parameters from an evolved population
            generated by the runFixedPop executable

        fixed_mass (float):
            Total mass sampled to generate the fixed population

        gx_component (string):
            Milky Way component for which we are generating the population
            realization; choose from 'ThinDisk', 'ThickDisk', 'Bulge'

        Returns
        -------
        n_samp (int):
            The number of systems in the Milky Way realization
        """

        # Compute the mass weighted number of systems 
        # in a realistic Milky Way pop
        #######################################################################
        component_mass = MC_sample.select_component_mass(self.gx_component)
        n_samp = MC_sample.mass_weighted_number(self.fixed_pop, self.fixed_mass, component_mass)
                 
        return n_samp


    def sample_population(self):
        """Once the fixed population is evolved, we Monte-Carlo
        sample the binary parameters to generate a Milky Way realization.

        Parameters
        ----------
        fixedpop (DataFrame): 
            Contains binary parameters from an evolved population
            generated by the runFixedPop executable

        n_samp (int):
            The number of systems in the Milky Way realization

        gx_component (string):
            Milky Way component for which we are generating the population 
            realization; choose from 'ThinDisk', 'ThickDisk', 'Bulge'
 
        gx_model (string):
            Model for spatial distribution of binaries in the Galactic 
            component; Default='McMillan'       
 
        dat_list (list):
            List containing the parameters to MC sample to generate the 
            Galactic realization

        Returns
        -------
        realization (DataFrame):
            Milky Way population realization of size n_samp
        """

        if not hasattr(self, 'n_samp'):
            self.n_samp = self.compute_n_sample()

        # Based on the user supplied filter flags, filter the
        # population to reduce the sample to only the relevant population
        #######################################################################
        #
        # Fill this in; holding place for now
        # 
        
        # Transform the fixed population to have limits between 0 and 1
        # then transform to logit space to maintain the population boundaries
        # and create a KDE using knuth's rule to select the bandwidth
        #######################################################################
        dat_kde = utils.dat_transform(self.fixed_pop, self.dat_list)
        bw = utils.knuth_bw_selector(dat_kde)
        dat_kernel = stats.gaussian_kde(dat_kde, bw_method=bw)
    
        # Sample from the KDE
        #######################################################################
        binary_dat_trans = dat_kernel.resample(self.n_samp)
        binary_dat = utils.dat_un_transform(binary_dat_trans, self.fixed_pop, self.dat_list)
        
        # Sample positions and orientations for each sampled binary
        #######################################################################
        binary_positions = MC_sample.galactic_positions(self.gx_component,
                                                        size = len(binary_dat[0]),
                                                        model=self.gx_model)
         
        # Create a single DataFrame for the Galactic realization
        #######################################################################
        realization = np.concatenate([binary_sample_dat,binary_sample_positions]).T
        column_list = dat_list + ['xGx', 'yGx', 'zGx', 'dist', 'inc', 'OMEGA', 'omega']
        realization = pd.DataFrame(full_sample,\
                                   columns = column_list) 

        
        return realization


    def LISA_obs(self, T_obs):
        """Computes the gravitational wave signal from the population
        that will be observable by LISA, including SNR and PSD according
        to the user input

        Parameters
        ----------
        realization (DataFrame):
            Milky Way population realization of size n_samp

        T_obs (float):
            LISA observation time in seconds

        Returns
        -------
        SNR_dat (DataFrame):
            DataFrame containing signal to noise ratios for all systems 
            in realization
 
        foreground_dat (DataFrame):
            DataFrame containing power spectral density of the population
            over a set of frequency bins with width set by the LISA 
            observation time           
        """

        # Compute the SNR
        ####################################################################### 
        SNR_dat = GW_calcs.SNR_calcs(self.realization.mass1*Msun, 
                                     self.realization.mass2*Msun,
                                     self.realization.porb*sec_in_year,
                                     self.realization.ecc, 
                                     self.realization.dist*1000*parsec,
                                     150)

        # Compute the PSD
        #######################################################################
        PSD_dat = GW_calcs.PSD_calcs(self.realization.mass1*Msun, 
                                     self.realization.mass2*Msun,
                                     self.realization.porb*sec_in_year,
                                     self.realization.ecc, 
                                     self.realization.dist*1000*parsec,
                                     150)
         # Compute the foreground from the PSD dataframe
         #######################################################################
         foreground_dat = GW_calcs.compute_foreground(PSD_dat, T_obs)

         return SNR_dat, foreground_dat
         
