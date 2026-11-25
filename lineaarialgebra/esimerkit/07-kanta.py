"""Lineaarinen riippumattomuus, kanta ja kannanvaihto."""

import numpy as np

# @alku riippumattomuus
# Vektorit ovat lineaarisesti riippumattomia, jos sarakkeista koottu
# matriisi on täysiasteinen. matrix_rank laskee asteen toleranssilla.
joukot = {
    "e1, e2, e3": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
    "u, v, u+v": [[1, 2, 0], [0, 1, 1], [1, 3, 1]],
    "u, v, w": [[1, 2, 0], [0, 1, 1], [1, 0, 1]],
}
for nimi, vektorit in joukot.items():
    A = np.array(vektorit, dtype=float).T
    aste = int(np.linalg.matrix_rank(A))
    tulos = "kanta" if aste == 3 else "riippuvia"
    print(f"{nimi:<11} aste {aste}: {tulos}")
# @loppu riippumattomuus

# @alku vari
# Värin RGB-koordinaatit vaihdetaan kantaan YCoCg: kirkkaus (Y) ja
# kaksi värieroa. Kuvanpakkaus säilyttää kirkkauden tarkemmin kuin
# värierot, koska silmä on tarkempi kirkkaudelle.
RGB_YCOCG = np.array([[0.25, 0.5, 0.25],
                      [0.5, 0.0, -0.5],
                      [-0.25, 0.5, -0.25]])
YCOCG_RGB = np.linalg.inv(RGB_YCOCG)
print("takaisinmuunnos:", (np.round(YCOCG_RGB, 3) + 0.0).tolist())
for nimi, rgb in [("valkoinen", [1.0, 1.0, 1.0]), ("punainen", [1.0, 0, 0]),
                  ("oranssi", [1.0, 0.5, 0.0])]:
    y, co, cg = RGB_YCOCG @ np.array(rgb)
    print(f"{nimi:<9} Y={y:5.3f} Co={co + 0.0:6.3f} Cg={cg + 0.0:6.3f}")
# @loppu vari

# @alku koordinaatit
# Saman vektorin koordinaatit kannassa B saadaan ratkaisemalla Bc = v.
B = np.array([[1.0, 1.0], [-1.0, 1.0]]).T        # kantavektorit sarakkeina
v = np.array([3.0, 1.0])
c = np.linalg.solve(B, v)
print("koordinaatit kannassa B:", (np.round(c, 6) + 0.0).tolist(),
      "-> B·c =", (np.round(B @ c, 6) + 0.0).tolist())
# @loppu koordinaatit
