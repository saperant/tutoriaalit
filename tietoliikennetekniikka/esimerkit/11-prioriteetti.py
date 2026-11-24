"""Prioriteettijono: puhe ohittaa tiedostonsiirron."""

import heapq

import numpy as np

LINKKI = 10e6 / 8          # tavua/s


# @alku jono
def simuloi(prioriteetti: bool, siemen: int = 5) -> dict[str, float]:
    rng = np.random.default_rng(siemen)
    tapahtumat: list[tuple[float, int, str, int]] = []
    # Puhe: 200 tavua 20 ms välein; tiedostonsiirto: 1500 tavun
    # paketteja purskeina, keskimäärin 85 % linkistä.
    for i in range(500):
        heapq.heappush(tapahtumat, (i * 0.02, i, "puhe", 200))
    t, i = 0.0, 500
    while t < 10.0:
        t += float(rng.exponential(1500 / (0.85 * LINKKI)))
        heapq.heappush(tapahtumat, (t, i, "data", 1500))
        i += 1
    jonossa: list[tuple[int, float, int, str, int]] = []
    vapaa, viiveet = 0.0, {"puhe": [0.0], "data": [0.0]}
    while tapahtumat or jonossa:
        if tapahtumat and (not jonossa or tapahtumat[0][0] <= vapaa):
            saapui, n, luokka, koko = heapq.heappop(tapahtumat)
            arvo = 0 if (prioriteetti and luokka == "puhe") else 1
            heapq.heappush(jonossa, (arvo, saapui, n, luokka, koko))
            continue
        _, saapui, _, luokka, koko = heapq.heappop(jonossa)
        alku = max(vapaa, saapui)
        vapaa = alku + koko / LINKKI
        viiveet[luokka].append(vapaa - saapui)
    return {k: float(np.percentile(v, 99)) * 1e3 for k, v in viiveet.items()}
# @loppu jono


for nimi, prio in (("FIFO", False), ("prioriteetti", True)):
    v = simuloi(prio)
    print(f"{nimi:<13} 99 % viiveistä alle: puhe {v['puhe']:6.1f} ms,"
          f" data {v['data']:6.1f} ms")
