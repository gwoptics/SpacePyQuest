import numpy as np
import pystq.sites as sites
import pystq.materials as materials
from random import randrange


class Detector:
   # Detector takes dictionary as argument. This can then be passed around.
   def __init__(self, dictionary={}):

      self.names = {}
      self.limits = {}
      self.parameters = {}
      self.tags = {}

      # define user actions as
      # set_action(key, name, limit, tag = "Other", parameter = -1):
      self.set_action('freqrange', 'Frequency range [loq(Hz)]',  (-4, 5), "Office", parameter = (0, 4))
      self.set_action('site', 'Location', None, 'Office', parameter =  sites.Jungle)
      self.set_action('depth', 'Depth [m]', (0.0, 1000.0), 'Environment')
      self.set_action('pumps', 'No. vacuum pumps', (1, 16), 'Environment')
      self.set_action('temperature', 'Temperature [K]', (1.0, 330.0), 'Environment')
      self.set_action('sus_stages', 'No. suspension stages', (1, 9), 'Suspension')
      self.set_action('sus_length', 'Suspension length [m]', (0.35, 5.0), 'Suspension')
      self.set_action('mirror_mass', 'Mirror mass [kg]', (5.0, 100.0), 'Suspension')
      self.set_action('power', 'Laser power [W]', (1.0, 200.0), 'Optics')
      self.set_action('material', 'Material', None,  'Optics',  parameter = materials.Silicon)
      self.set_action('roughness', 'Roughness [nm]', (1, 500), 'Optics') 
      
      # Now set random initial values based on constraints in self.limits.
      # Do float for float limits, int for int limits and nothing for others
      for key in self.limits:
          if type(self.limits[key]) is float:
             lim_diff = self.limits[key][1] - self.limits[key][0]
             rand_float = float(randrange(1, 100)) / 100.0
             self.parameters[key] = self.limits[key][0] + rand_float * lim_diff
          if type(self.limits[key]) is int:
             lim_diff = self.limits[key][1] - self.limits[key][0]
             rand_float = float(randrange(1, 100)) / 100.0
             self.parameters[key] = int(self.limits[key][0] + rand_float * lim_diff)
                 
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
      
   def set_action(self, key, name, limit, tag = "Other", parameter = -1):
      self.names[key] = name
      if limit is not None:
          self.limits[key] = limit
      self.parameters[key] = parameter
      self.tags[key] = tag
