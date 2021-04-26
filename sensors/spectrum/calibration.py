"""
Light source: warm white 2700K LED
Irradiance: Ee = 107.67μW/cm2
Sensor config: AGAIN: 64x, Integration Time: 27.8ms
"""

CALIBRATION = {
    "channel_415nm": 55,
    "channel_445nm": 110,
    "channel_480nm": 210,
    "channel_515nm": 390,
    "channel_555nm": 590,
    "channel_590nm": 840,
    "channel_630nm": 1350,
    "channel_680nm": 1070,
    "channel_CLEAR": 1750,
    "channel_NIR": 112,
}

CONST = {
    "irradiance": 107.67,
    "integration_ms": 27.8,
    "Planck": 6.62607015e-34,
    "Avogadro": 6.02214076e23,
    "lightspeed": 299792458,
}
