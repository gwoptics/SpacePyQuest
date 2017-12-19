import numpy as np
import pystq.constants as constants
import pystq.materials as materials

class GravityGradientNoise:

    @staticmethod
    def GetGravityGradientNoise(f, detector):
        # seismic noise
        X_0 = detector.parameters['site'].X_dc / (1 + np.power(f / detector.parameters['site'].f_c, detector.parameters['site'].n_0))
        # reduction of seismic noise suppression due to digging
        X_0 = X_0 + detector.parameters['site'].X_hf
        dig = 1 / np.sqrt(1 + np.power(detector.parameters['depth'] / 50, 4)) + 0.8E-3
        return X_0 * dig * 1.3E-8 / detector.constants['L'] / np.power(f, 2)

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetGravityGradientNoise(f, detector)


class MirrorThermalNoise:

    @staticmethod
    def GetMirrorThermalNoise(f, detector):
        K1 = np.sqrt(4) / detector.constants['L'] * np.sqrt(4 * constants.kb)
        M_eff = 0.28 * detector.parameters['mirror_mass']
        omega = np.pi * 2 * f
        omega1 = np.pi * 2 * 20505 * np.power(23 / detector.parameters['mirror_mass'], 0.66)
        return K1 * np.sqrt(detector.parameters['temperature'] * omega1**2
            / (omega * M_eff * detector.parameters['material'].GetQ(detector)
                * ((omega1**2 - omega**2)**2 + (omega1**2 / detector.parameters['material'].GetQ(detector))**2)
            ))

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetMirrorThermalNoise(f, detector)

class RadiationPressureNoise:

    @staticmethod
    def GetRadiationPressureNoise(f, detector):
        K1 = np.sqrt(8 * detector.constants['C'] * constants.h / (constants.c * detector.constants['Lambda'])) * detector.constants['F'] / detector.constants['L'] / np.power(np.pi, 2)
        K2 = (constants.c / 4 / detector.constants['L'] / detector.constants['F'])
        return K1 * (np.sqrt(detector.parameters['power']) /
            detector.parameters['mirror_mass'] / (f * f) /
            np.sqrt(1 + f * f / K2 / K2) *
            np.sqrt(detector.parameters['material'].losses) *
            np.sqrt(materials.GetRoughnessLoss(detector.parameters['roughness'])))

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetRadiationPressureNoise(f, detector)

class ResidualGas:
    @staticmethod
    def GetResidualGas(detector):
        n = detector.parameters['pumps']
        pressure = (constants.atmospherePressure * np.exp(-8.0 * n) +
                    10 * np.exp(-4.0 * n) +
                    1E-3 * np.exp(-2.0 * n) +
                    1E-8 * np.exp(-0.7 * n) +
                    1E-11 * np.exp(-0.3 * n) +
                    1E-16)
        return 1.37E-18 * np.sqrt(pressure / detector.constants['L'])

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetResidualGas(detector)

class SeismicNoise:

    @staticmethod
    def GetSeismicNoise(f, detector):
        Q_pend = 5 # use highly damped pendulum
        # seismic noise
        X_0 = detector.parameters['site'].X_dc / (1 + np.power(f / detector.parameters['site'].f_c, detector.parameters['site'].n_0))
        # reduction of seismic noise suppression due to digging
        X_0 = X_0 + detector.parameters['site'].X_hf
        dig = 1 / np.sqrt(1 + np.power(detector.parameters['depth'] / 50, 4)) + 0.8E-3

        # pendulum resonance
        f_pend = np.power(constants.g / detector.parameters['sus_length'], 0.5) / (np.pi * 2)
        # pendulum transfer function
        pend_tf = np.power(1 + np.power(f / f_pend, 4) - (2 - 1 / Q_pend) * np.power(f / f_pend, 2), -detector.parameters['sus_stages'] / 2)
        return X_0 * 2 / detector.constants['L'] * dig * pend_tf

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetSeismicNoise(f, detector)

class ShotNoise:

    @staticmethod
    def GetShotNoise(f, detector):
        K1 = (1 / (8 * detector.constants['L'] * detector.constants['F'])) * np.sqrt((2 * constants.h * detector.constants['Lambda'] * constants.c) / detector.constants['C'])
        K2 = (4 * detector.constants['L'] * detector.constants['F'] / constants.c) * (4 * detector.constants['L'] * detector.constants['F'] / constants.c)
        return K1 * (np.sqrt(1 + K2 * f * f) / np.sqrt(detector.parameters['power'] * detector.parameters['material'].losses)
                / (np.power(materials.GetRoughnessLoss(detector.parameters['roughness']), 5)))

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetShotNoise(f, detector)

class SuspThermalNoise:

    @staticmethod
    def GetSuspThermalNoise(f, detector):
        E = 2E11 # youngs modulus
        Y = 2E9 # breaking strength
        phi = 1e-4 # loss angle

        K1 = 2 / detector.constants['L'] * np.sqrt(4 * constants.kb * constants.g / 4 * np.sqrt(constants.g * E / np.pi) * phi / Y)
        return (K1
            * np.sqrt(detector.parameters['temperature'])
            / np.sqrt(np.power(np.pi * 2 * f, 5))
            / np.sqrt(np.power(detector.parameters['sus_length'], 2))
            / np.sqrt(np.sqrt(detector.parameters['mirror_mass'])))

    @classmethod
    def ComputePoint(cls, f, detector):
        return cls.GetSuspThermalNoise(f, detector)

class TotalNoise:

    @staticmethod
    def ComputePoint(f, detector):
        A = GravityGradientNoise.GetGravityGradientNoise(f, detector)
        B = RadiationPressureNoise.GetRadiationPressureNoise(f, detector)
        C = ResidualGas.GetResidualGas(detector)
        D = MirrorThermalNoise.GetMirrorThermalNoise(f, detector)
        E = SeismicNoise.GetSeismicNoise(f, detector)
        F = ShotNoise.GetShotNoise(f, detector)
        G = SuspThermalNoise.GetSuspThermalNoise(f, detector)

        return np.sqrt(A * A + B * B + C * C + D * D + E * E + F * F + G * G)

