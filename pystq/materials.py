import numpy as np
import pystq.utils as utils


class Sapphire:
   losses = 1

   def GetQ(detector):
      return 1.0 / utils.LerpArray(sapphireLoss_x, sapphireLoss_y,
                                   detector.parameters['temperature'])

   def GetCost(detector):
      return 4e6 + 56e6 * (detector.parameters['mirror_mass'] / 100)**2


class Crystal:
   losses = 0.4

   def GetQ(detector):
      return 1.0 / utils.LerpArray(crystalLoss_x, crystalLoss_y,
                                   detector.parameters['temperature'])

   def GetCost(detector):
      return 5e5 + 9.5e6 * (detector.parameters['mirror_mass'] / 100)**2


class Silicon:
   losses = 1

   def GetQ(detector):
      return 1.0 / utils.LerpArray(siliconLoss_x, siliconLoss_y,
                                   detector.parameters['temperature'])

   def GetCost(detector):
      return 2e6 + 38e6 * (detector.parameters['mirror_mass'] / 100)**2


class Silica:
   losses = 1

   def GetQ(detector):
      return 1.0 / utils.LerpArray(silicaLoss_x, silicaLoss_y,
                                   detector.parameters['temperature'])

   def GetCost(detector):
      return 1.5e6 + 28.5e6 * (detector.parameters['mirror_mass'] / 100)**2


def GetRoughnessLoss(roughness):
   return (1 + 0.9 / 499) - roughness / 499 * 0.9


# Actual data values of material q as a function of temperature
silicaLoss_x = np.array([1, 35, 90, 150, 200, 250, 300])
silicaLoss_y = np.array([1e-3, 7e-4, 1e-4, 3e-6, 3e-7, 1.5e-7, 1.5e-7])
siliconLoss_x = np.array([1, 32, 40, 270, 300])
siliconLoss_y = np.array([1.4e-9, 1.5e-8, 7.5e-9, 4.5e-8, 7e-8])
crystalLoss_x = np.array([1, 300])
crystalLoss_y = np.array([1e-3, 1e-3])
sapphireLoss_x = np.array([1, 25, 80, 105, 230, 300])
sapphireLoss_y = np.array([1.4e-9, 2.5e-8, 7e-9, 1.2e-8, 1.6e-8, 1e-7])
