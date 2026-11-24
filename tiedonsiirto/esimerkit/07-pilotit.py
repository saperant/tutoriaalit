"""OFDM:n kanavaestimointi kampapiloteista ja interpolointi."""

import numpy as np

rng = np.random.default_rng(19)
N, cp, symboleja = 64, 16, 200
kanava = np.array([0.8, 0, 0.5, 0.3j, 0, 0, 0.2, 0.1])
H = np.fft.fft(kanava, N)

# @alku pilotit
# Joka neljäs alikantoaalto on pilotti, jonka arvo (1) tunnetaan.
pilotit = np.arange(0, N, 4)
data_k = np.setdiff1d(np.arange(N), pilotit)
b = rng.integers(0, 2, (2, symboleja, N))
X = ((1 - 2 * b[0]) + 1j * (1 - 2 * b[1])) / np.sqrt(2)
X[:, pilotit] = 1.0

x = np.fft.ifft(X, axis=1) * np.sqrt(N)
x = np.hstack([x[:, N - cp:], x]).ravel()
r = np.convolve(x, kanava)[: len(x)]
r += 10 ** (-25 / 20) * (rng.standard_normal(len(r))
                         + 1j * rng.standard_normal(len(r))) / np.sqrt(2)
Y = np.fft.fft(r.reshape(symboleja, N + cp)[:, cp:], axis=1) / np.sqrt(N)
# @loppu pilotit


# @alku estimoi
def evm(H_arvio: np.ndarray) -> float:
    """Datakantoaaltojen EVM, kun taajuuskorjaus tehdään arviolla."""
    tasattu = Y[:, data_k] / H_arvio[:, data_k]
    return float(np.sqrt(np.mean(np.abs(tasattu - X[:, data_k]) ** 2)))


# Pilottien kohdalla kanava on Y / X; muualla interpoloidaan.
H_p = Y[:, pilotit] / X[:, pilotit]
k = np.arange(N)
lineaarinen = np.array([np.interp(k, pilotit, h.real)
                        + 1j * np.interp(k, pilotit, h.imag) for h in H_p])
# Kanavan impulssivaste on lyhyt: pilottien IFFT antaa sen suoraan, kun
# pilotteja on enemmän kuin vasteessa on näytteitä (16 > 8). Vain 8
# ensimmäistä näytettä pidetään; loput ovat pelkkää kohinaa.
h_arvio = np.fft.ifft(H_p, axis=1)[:, :8]
aikataso = np.fft.fft(h_arvio, N, axis=1)
# Kanava ei muutu, joten estimaatin voi keskiarvoistaa symbolien yli.
keskiarvo = np.tile(aikataso.mean(axis=0), (symboleja, 1))
for nimi, arvio in (("tunnettu kanava", np.tile(H, (symboleja, 1))),
                    ("lineaarinen interpolointi", lineaarinen),
                    ("aikatason rajaus", aikataso),
                    ("rajaus + keskiarvo 200", keskiarvo)):
    print(f"{nimi:26s} EVM {100 * evm(arvio):5.1f} %")
# @loppu estimoi
