import numpy as np
import pystq.sites as sites
import pystq.materials as materials
from random import randrange

class Detector:
    # Detector takes dictionary as argument. This can then be passed around.
    def __init__(self, dictionary={}):

        self.names = {}
        self.names['freqrange'] = 'Frequency range [loq(Hz)]'
        self.names['site'] = 'Location'
        self.names['depth'] = 'Depth [m]'
        self.names['pumps'] = 'No. vacuum pumps'
        self.names['temperature'] = 'Temperature [K]'
        self.names['sus_stages'] = 'No. suspension stages'
        self.names['sus_length'] = 'Suspension length [m]'
        self.names['mirror_mass'] = 'Mirror mass [kg]'
        self.names['power'] = 'Laser power [W]'
        self.names['material'] = 'Material'
        self.names['roughness'] = 'Roughness [nm]'

        self.limits = {}
        # Frequency (Hz)
        self.limits['freqrange'] = (-4, 5)
        # Depth (m)
        self.limits['depth'] = (0, 1000)
        # Number of vacuum pumps
        self.limits['pumps'] = (0, 16)
        # Temperature (K)
        self.limits['temperature'] = (1, 330)
        # Number of suspension stages
        self.limits['sus_stages'] = (1, 9)
        # Length of suspension (m)
        self.limits['sus_length'] = (0.35, 5)
        # Mirror mass (kg)
        self.limits['mirror_mass'] = (5, 100)
        # Laser power (W)
        self.limits['power'] = (0, 200)
        # Roughness (nm)
        self.limits['roughness'] = (1, 500)

        # Set initial values, which might be changed by input dictionary.
        self.parameters = {}
        # Initially set numeric values to obviously erroneous values.
        self.parameters['depth'] = -1
        self.parameters['pumps'] = -1
        self.parameters['temperature'] = -1
        self.parameters['sus_stages'] = -1
        self.parameters['sus_length'] = -1
        self.parameters['mirror_mass'] = -1
        self.parameters['power'] = -1
        self.parameters['roughness'] = -1
        # Now set random initial values based on constraints in self.limits.
        for key in self.limits:
            lim_diff = self.limits[key][1]-self.limits[key][0]
            rand_float = float(randrange(1,100))/100.0
            self.parameters[key] = self.limits[key][0]+rand_float*lim_diff
        # IRS TODO: Have to do frequency range afterwards to get tuple: 
        # possibly find fix.
        # IRS TODO: Randomise these.
        self.parameters['freqrange'] = (0, 4)
        self.parameters['site'] = sites.Jungle
        self.parameters['material'] = materials.Silicon
        self.parameters['sus_stages'] = int(self.parameters['sus_stages'])

        # Now update based on input dictionary
        for key in dictionary:
            self.parameters[key] = dictionary[key]

        # Other, constant parameters
        self.constants = {}
        # Detector Length (m) 
        self.constants['L'] = 5000
        # Detector Finesse 
        self.constants['F'] = 60
        # Laser Wavelength (m) 
        self.constants['Lambda'] = 1064E-9
        # Detector Power Recycling factor 
        self.constants['C'] = 100
        # First Mirror Resonance (Hz) 
        self.constants['fmr'] = 4000
        # Vacuum pump cost
        self.constants['vacuumPumpCost'] = 850000
        # Initial ambient temperature (K)
        self.constants['initAmbientTemp'] = 300
        # Temperature increase per km (K)
        self.constants['tempIncPerKm'] = 30
        # Depth complexity, X
        self.constants['depthComplexityX'] = np.array([0, 10, 100, 500])
        # Depth complexity, Y
        self.constants['depthComplexityY'] = np.array([0, 1, 4, 6])

        self.options = {}
        self.options['material'] = ['Crystal', 'Silicon', 'Sapphire', 'Silica']
        self.options['site'] = ['City', 'Jungle', 'Desert', 'Island']


    def setParameter(self, key, value, name=None):
        self.parameters[key] = value
        if type(name) != None:
            self.names[key] = name