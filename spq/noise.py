import numpy as np
import pystq.constants as constants
import pystq.materials as materials


# Functions that are shared between multiple noise models
#-----------------------------------------------------------------------------#
def getXSeis(f, detector):
   # seismic noise
   X_0 = detector.parameters['site'].X_dc/\
                          (1 + np.power(f/ \
                           detector.parameters['site'].f_c, \
                           detector.parameters['site'].n_0))
   # reduction of seismic noise suppression due to digging
   X_0 = X_0 + detector.parameters['site'].X_hf
   dig = 1 / np.sqrt(
      1 + np.power(detector.parameters['depth'] / 50, 4)) + 0.8E-3
   return X_0 * dig


def getFPfreq(detector):
   return constants.c / (4 * detector.constants['L'] * detector.constants['F'])


#-----------------------------------------------------------------------------#


class GravityGradientNoise:

   @staticmethod
   def GetGravityGradientNoise(f, detector):
      X_seis = getXSeis(f, detector)
      return X_seis * 1.3E-8 / detector.constants['L'] / np.power(f, 2)

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetGravityGradientNoise(f, detector)


class SeismicNoise:

   @staticmethod
   def GetSeismicNoise(f, detector):
      Q_pend = 5  # use highly damped pendulum
      X_seis = getXSeis(f, detector)
      # pendulum resonance
      f_pend = np.power(constants.g / detector.parameters['sus_length'],
                        0.5) / (np.pi * 2)
      # pendulum transfer function
      pend_tf = np.power(1 + np.power(f/f_pend, 4) - (2 - 1/Q_pend) \
             *np.power(f/f_pend, 2), -detector.parameters['sus_stages']/2)
      return X_seis * 2 / detector.constants['L'] * pend_tf

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetSeismicNoise(f, detector)


class MirrorThermalNoise:

   @staticmethod
   def GetMirrorThermalNoise(f, detector):
      K1 = np.sqrt(4) / detector.constants['L'] * np.sqrt(4 * constants.kb)
      M_eff = 0.28 * detector.parameters['mirror_mass']
      omega = np.pi * 2 * f
      omega1 = np.pi * 2 * 20505 * np.power(
         23 / detector.parameters['mirror_mass'], 0.66)
      return K1*np.sqrt(detector.parameters['temperature']*omega1**2
         /(omega*M_eff*detector.parameters['material'].GetQ(detector)
             *((omega1**2 - omega**2)**2 + (omega1**2/\
                  detector.parameters['material'].GetQ(detector))**2)
          ))

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetMirrorThermalNoise(f, detector)


class RadiationPressureNoise:

   @staticmethod
   def GetRadiationPressureNoise(f, detector):
      K1 = np.sqrt(8*detector.constants['C']*constants.h /\
                  (constants.c*detector.constants['Lambda']))*\
                   detector.constants['F']/detector.constants['L'] /\
                    np.power(np.pi, 3)
      K2 = getFPfreq(detector)
      return K1 * (np.sqrt(detector.parameters['power']) / detector.parameters[
         'mirror_mass'] / (f * f) / np.sqrt(1 + f * f / K2 / K2) * np.sqrt(
            detector.parameters['material'].losses) * np.sqrt(
               materials.GetRoughnessLoss(detector.parameters['roughness'])))

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetRadiationPressureNoise(f, detector)


class ResidualGas:

   @staticmethod
   def GetResidualGas(detector):
      n = detector.parameters['pumps']
      pressure = (constants.atmospherePressure * np.exp(-8.0 * n) +
                  10 * np.exp(-4.0 * n) + 1E-3 * np.exp(-2.0 * n) +
                  1E-8 * np.exp(-0.7 * n) + 1E-11 * np.exp(-0.3 * n) + 1E-16)
      return 1.37E-18 * np.sqrt(pressure / detector.constants['L'])

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetResidualGas(detector)


class ShotNoise:

   @staticmethod
   def GetShotNoise(f, detector):
      K1 = (1/(8*detector.constants['L']*detector.constants['F'])) \
          *np.sqrt((2*constants.h*detector.constants['Lambda']*constants.c) /\
             detector.constants['C'])
      K2 = pow(getFPfreq(detector), -2)
      return K1*(np.sqrt(1 + K2*f*f)/np.sqrt(detector.parameters['power'] *\
              detector.parameters['material'].losses)
             /(np.power(materials.GetRoughnessLoss(detector.parameters['roughness']), 5)))

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetShotNoise(f, detector)


class SuspThermalNoise:

   @staticmethod
   def GetSuspThermalNoise(f, detector):
      E = 2E11  # youngs modulus
      Y = 2E9  # breaking strength
      phi = 1e-4  # loss angle

      K1 = 2/detector.constants['L']*np.sqrt(4*constants.kb*constants.g/\
          4*np.sqrt(constants.g*E/np.pi)*phi/Y)
      return (K1 * np.sqrt(detector.parameters['temperature']) / np.sqrt(
         np.power(np.pi * 2 * f, 5)) / np.sqrt(
            np.power(detector.parameters['sus_length'], 2)) / np.sqrt(
               np.sqrt(detector.parameters['mirror_mass'])))

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetSuspThermalNoise(f, detector)
