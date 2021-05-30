CONST = {
    "normal_tint_ms": 1000,
    "normal_gain": 64,
    "relative_gains": {
        "415nm": 0.1663865546,
        "445nm": 0.3036414566,
        "480nm": 0.3792717087,
        "515nm": 0.4857142857,
        "555nm": 0.5865546218,
        "590nm": 0.6537815126,
        "630nm": 0.7602240896,
        "680nm": 0.9983193277,
        "NIR": 1.6067226891,
        "CLEAR": 0.4417366947,
    },
}


def get_photon_energy(wavelength):
    h = 6.6260695e-34
    c = 299792458
    return h * c / (wavelength * 1e-9)


def get_relative_photon_energies(channels):
    photon_energies = {}
    for channel in channels:
        if "nm" in channel:
            wavelength = int(channel.split("nm")[0])
            photon_energies[channel] = get_photon_energy(wavelength)
    max_photon_energy = max(photon_energies.values())

    relative_photon_energies = {}
    for channel in channels:
        if "nm" in channel:
            relative_photon_energies[channel] = photon_energies[channel] / max_photon_energy

    return relative_photon_energies


CONST["relative_photon_energies"] = get_relative_photon_energies(CONST["relative_gains"])
print(CONST)