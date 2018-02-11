# Represents a user who knows how the code works, but doesn't want to
# tamper with it and risk breaking it.

# They define one new noise, and rewrite another.


class GravGrad:
   # Rewrites GravityGradientNoise
   @staticmethod
   def GetGravGrad(f, detector):
      return detector.parameters['sus_stages'] * detector.parameters[
         'pumps'] * 1E-22 / f

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetGravGrad(f, detector)


class AlienLandingNoise:
   # Models the noise from an alien spaceship landing on the detector
   @staticmethod
   def GetAlienLandingNoise(f, detector):
      return 1E-23

   @classmethod
   def ComputePoint(cls, f, detector):
      return cls.GetAlienLandingNoise(f, detector)