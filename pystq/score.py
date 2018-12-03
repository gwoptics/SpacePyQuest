import numpy as np
import pystq.constants as constants
import pystq.utils as utils
from pystq.noise import *
from pystq.materials import GetRoughnessLoss
import scipy.integrate as integrate


def CalcComplex(detector):
   # Environment
   depthComplex = utils.LerpArray(detector.constants['depthComplexityX'], \
                                  detector.constants['depthComplexityY'], \
                                  detector.parameters['depth'])
   vacuumComplex = detector.parameters['pumps'] / 10

   if detector.parameters['temperature'] > constants.nitrogenTemp:
      coolingComplex = 1 - (detector.parameters['temperature'] - constants.nitrogenTemp)/\
      (detector.constants['initAmbientTemp'] +
              detector.constants['tempIncPerKm'] * detector.parameters['depth'] /\
               1000 - constants.nitrogenTemp)
   else:
      coolingComplex = 5

   # Vibration
   stagesComplex = detector.parameters['sus_stages'] / 2
   massComplex = detector.parameters['mirror_mass'] / 50

   # Optics
   powerComplex = detector.parameters['power'] / 10
   materialComplex = detector.parameters['material'].losses
   roughnessComplex = 1 + (50 - detector.parameters['roughness']) / 500

   return (depthComplex + vacuumComplex + coolingComplex + stagesComplex +
           massComplex + powerComplex + materialComplex + roughnessComplex)


def CalcCost(detector):
   # Environment
   depthCosts = np.power(max(
      (detector.parameters['depth'] - 20), 0), 1 / 3) * 75E5
   vacuumCosts = detector.parameters['pumps'] * detector.constants[
      'vacuumPumpCost']
   if detector.parameters['temperature'] > constants.nitrogenTemp:
      K0 = 0
      K1 = 20102
      K2 = detector.constants['initAmbientTemp'] + \
      detector.constants['tempIncPerKm'] * detector.parameters['depth'] / 1000
      coolingCosts = K0 + K1 * (K2 - detector.parameters['temperature'])
   else:
      K2 = 77
      K1 = 10201
      K0 = 7000000
      coolingCosts = K0 + K1 * (K2 - detector.parameters['temperature'])**2

   # Vibration
   vibrationCosts = (detector.parameters['sus_length']**2.1 * detector.
                     parameters['sus_stages']**5.5 * detector.
                     parameters['mirror_mass']**1.2) * 60 - 60

   # Optics
   powerCosts = 47000 + 25e6 * (
      detector.parameters['power'] / detector.limits['power'][1])**2
   matCosts = detector.parameters['material'].GetCost(detector)
   roughnessCosts = (detector.parameters['mirror_mass']**(2 / 3) *
                     (GetRoughnessLoss(detector.parameters['roughness'])**3 -
                      GetRoughnessLoss(500)**3) / 25 * 8e7)

   return (depthCosts + vacuumCosts + coolingCosts + vibrationCosts +
           powerCosts + matCosts + roughnessCosts)


class Score:

   def __init__(self):
      self.bhbh = 0
      self.nsns = 0
      self.supernovae = 0
      self.bhbhRange = 0
      self.nsnsRange = 0


class ScoreCalculator:

   def __init__(self, detector):
      self.detector = detector

      # Integral values
      self.fMin = pow(10, detector.parameters['freqrange'][0])
      self.fMax = pow(10, detector.parameters['freqrange'][1])
      # TODO: fix this
      # adf 14.02.2018, set nData from 100 to 1000
      # workaround for Bokeh bug, see widget.py
      self.nData = 1000

      # Dictionary containing noise models
      self.noiseModels = {}
      self.noiseModels['Residual Gas'] = ResidualGas()
      self.noiseModels['Mirror Thermal'] = MirrorThermalNoise()
      self.noiseModels['Radiation Pressure'] = RadiationPressureNoise()
      self.noiseModels['Seismic'] = SeismicNoise()
      self.noiseModels['Shot'] = ShotNoise()
      self.noiseModels['Gravity Gradient'] = GravityGradientNoise()
      self.noiseModels['Suspension Thermal'] = SuspThermalNoise()
      # And another one dictating which we actually use in calculations
      self.noisesUsed = {}
      self.noisesUsed['Residual Gas'] = True
      self.noisesUsed['Mirror Thermal'] = True
      self.noisesUsed['Radiation Pressure'] = True
      self.noisesUsed['Seismic'] = True
      self.noisesUsed['Shot'] = True
      self.noisesUsed['Gravity Gradient'] = True
      self.noisesUsed['Suspension Thermal'] = True

   # Setter for frequency range
   def SetFreqRange(self, fLo, fHi):
      self.fMin = pow(10, fLo)
      self.fMax = pow(10, fHi)

   # Setter for True/False values of noisesUsed
   def SetNoiseUsed(self, key, valueTF):
      self.noisesUsed[key] = valueTF

   # Function to assign a new noise model to a key in noiseModels.
   # Can be used both to overwrite existing models, and to add new ones.
   def SetNoiseModels(self, newNoiseDict):
      for key in newNoiseDict:
         self.noiseModels[key] = newNoiseDict[key]
         self.SetNoiseUsed(key, True)

   def GetDetectorDistance(self, m1, m2):
      snr_threshold = 8

      nu_Mpc = constants.Distances['MPC'] / constants.c
      nu_Msun = constants.Msun * constants.G / (constants.c)**3

      # Note: This function assumes natural units where G == c == 1. For
      # this reason Mpc and Msun are converted to seconds above.
      # Keplerian orbital frequency at the innermost stable circular orbit.
      # At this point the GW signal shuts off (for BNS) or transitions into
      # merger and ringdown (NSBH & BBH)
      # [Ref 2, page 7, between equations 2.21 and 2.22]
      f_isco = 1 / (np.power(6, 1.5) * np.pi * (m1 + m2) * nu_Msun)
      # Chirp mass: (m1*m2)**(3/5) / (m1+m2)**(1/5)
      m_chirp = (np.power(m1 * m2, 0.6) / np.power(m1 + m2, 0.2)) * nu_Msun
      # Constant containing all components of 3.16 except f_{7/3}, where
      # the equation has been solved for d_L and the SNR threshold of
      # 8 is used as SNR value. A is defined in Ref 1, equation 3.30.
      # 16 is the maximum value of $\Theta^2$ [Page 10, after equation 3.31]
      # which corresponds to the loudest possible signal.
      tmp = 5 * np.power(m_chirp, 5/3) * 16 / (96 * np.power(np.pi, 4/3) * \
            np.power(snr_threshold, 2))
      # Mask used to integrate only the range from f_low to f_isco
      #criterion = (freq > f_low)*(freq < f_isco)
      #assert f_low >= min(freq)
      #assert f_isco <= max(freq)
      # Integral over 1/(f**(7/3)*S_n(f)) [Ref 1, page 8, equation 3.18]
      # Note the '**2' used on noiseamp: be careful whether noiseamp
      # is the ASD or PSD. The current code is checked against the
      # observing scenarios paper.
      freq73 = self.CalcSensitivityIntegral(self.fMin, f_isco)
      # Combining the terms and converting the result into physical units.
      return np.sqrt(tmp * freq73) / nu_Mpc / 2.26

   def SensitivityLine(self, f):
      usedNoises = []
      for key in self.noisesUsed:
         if self.noisesUsed[key]:
            usedNoises.append(self.noiseModels[key])
      return sum(
         [model.ComputePoint(f, self.detector)**2 for model in usedNoises])

   def CalcSensitivityIntegral(self, f_1, f_2):

      def y_func(freq):
         return np.power(freq, -7 / 3) / self.SensitivityLine(freq)

      f_1 = np.log10(f_1)
      f_2 = np.log10(f_2)

      f = np.logspace(f_1, f_2, num=self.nData)
      y = y_func(f)

      I = integrate.simps(y, f)

      return I

   # Function to compute and return individual noise, plus total noise.
   def GetNoiseCurves(self):

      curves = {}
      for key in self.noiseModels:
         if self.noisesUsed[key]:
            curves[key] = []
      total = []
      f_out = []
      f_1 = np.log10(self.fMin)
      f_2 = np.log10(self.fMax)
      f_range = np.logspace(f_1, f_2, num=self.nData)
      for f in f_range[0:self.nData]:

         f_out.append(f)
         for key in curves:
            curves[key].append(self.noiseModels[key].ComputePoint(
               f, self.detector))
         total.append(np.sqrt(self.SensitivityLine(f)))
      # Ensure that total is placed last on any list
      curveList = [curves[key] for key in curves]
      curveList.append(total)
      nameList = [key for key in curves]
      nameList.append('Total')
      return f_out, curveList, nameList

   def Supernovae(self):

      f_1 = np.log10(self.fMin)
      f_2 = np.log10(self.fMax)

      def yn_func(freq):
         return np.sqrt(self.SensitivityLine(freq))

      def ys_func(freq):
         return np.sqrt(self.SensitivityLine(freq) + np.power(1E-23, 2))

      f = np.logspace(f_1, f_2, num=self.nData)
      yn = yn_func(f)
      ys = ys_func(f)

      In = integrate.simps(yn, f)

      Is = integrate.simps(ys, f)

      excess = max(0, Is - In)

      if (np.power(excess / 4E-20, 3) * 25) >= 1:
         return 1
      else:
         return 0

   def CalcNumNSNS(self, R):
      return (round(4 / 3 * np.pi * np.power(R / 1E3, 3) * 6000 * 1 / 12))

   def CalcNumBHBH(self, R):
      return (round(4 / 3 * np.pi * np.power(R / 1E3, 3) * 20 * 1 / 12))

   def CalcScore(self):
      score = Score()
      score.nsnsRange = self.GetDetectorDistance(1.7, 1.7)
      score.bhbhRange = self.GetDetectorDistance(47, 47)

      # Number of detections, we aribitrarily assume a run length of 1/200 year
      # 1) BNS,  we pick (randonmly) a rate of 6000 Gpc^-3 yr^-1
      # take the output from horzon_distance, convert to Gpc, cube, and then multiply with rate

      score.nsns = self.CalcNumNSNS(score.nsnsRange)

      # 2) heavy BBH
      score.bhbh = self.CalcNumBHBH(score.bhbhRange)

      # 3) self made SN number
      score.supernovae = self.Supernovae()

      # Weighted score distance
      score.score = np.sqrt(score.nsnsRange**2 + (score.bhbhRange / 10)**2)

      # Missed sources
      overComplex = max(0,
                        CalcComplex(self.detector) -
                        self.detector.parameters['site'].complexCredits)
      complexScale = 1 - overComplex / self.detector.parameters['site'].complexCredits
      score.supernovaeMissed = int(
         max(0, np.floor(score.supernovae * (1 - complexScale))))
      score.nsnsMissed = int(max(0, np.floor(score.nsns * (1 - complexScale))))
      score.bhbhMissed = int(max(0, np.floor(score.bhbh * (1 - complexScale))))
      return score
