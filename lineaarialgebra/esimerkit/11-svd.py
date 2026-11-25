"""Singulaariarvohajotelma A = U S V^T: kierto, venytys ja kierto."""

import numpy as np

# @alku hajotelma
A = np.array([[2.0, 1.0],
              [0.5, 1.5]])
U, s, Vt = np.linalg.svd(A)
print("singulaariarvot:", np.round(s, 4).tolist())
print("A = U S V^T:", bool(np.allclose(U @ np.diag(s) @ Vt, A)))
print("U ja V ortogonaalisia:",
      bool(np.allclose(U.T @ U, np.eye(2))
           and np.allclose(Vt @ Vt.T, np.eye(2))))
# A vie suunnan v_i suunnaksi u_i ja venyttää sitä kertoimella s_i.
for i in range(2):
    print(f"A v{i + 1} = s{i + 1} u{i + 1}:",
          bool(np.allclose(A @ Vt[i], s[i] * U[:, i])))
# Yksikköympyrän kuva on ellipsi, jonka puoliakselit ovat s1 ja s2.
kulmat = np.linspace(0.0, 2 * np.pi, 3601)
ympyra = np.vstack([np.cos(kulmat), np.sin(kulmat)])
pituudet = np.linalg.norm(A @ ympyra, axis=0)
print(f"ellipsin pisin säde {pituudet.max():.4f},",
      f"lyhin {pituudet.min():.4f}")
print(f"|det A| = {abs(np.linalg.det(A)):.4f} = s1 s2 = {s[0] * s[1]:.4f}")
# @loppu hajotelma

# @alku ominaisarvot
# Singulaariarvot ovat symmetrisen matriisin A^T A ominaisarvojen
# neliöjuuret, ja V:n sarakkeet ovat sen ominaisvektorit.
arvot, vektorit = np.linalg.eigh(A.T @ A)        # nousevassa järj.
print("sqrt(eig(A^T A)):", np.round(np.sqrt(arvot[::-1]), 4).tolist())
print("ominaisvektorit = V:n sarakkeet (etumerkkiä vaille):",
      bool(np.allclose(np.abs(vektorit[:, ::-1].T @ Vt.T), np.eye(2))))
# @loppu ominaisarvot

# @alku aste
# Aste on nollasta poikkeavien singulaariarvojen määrä. Liukuluvuilla
# "nolla" on pieni luku, joten raja on toleranssi.
B = np.array([[1.0, 0.0, 1.0],
              [2.0, 1.0, 3.0],
              [0.0, 1.0, 1.0]])            # 3. sarake = 1. + 2.
sb = np.linalg.svd(B, compute_uv=False)
toleranssi = sb[0] * 3 * np.finfo(float).eps
print("B:n singulaariarvot:", [f"{x:.3g}" if x > 1e-12 else "~0"
                               for x in sb])
print("aste:", int(np.sum(sb > toleranssi)),
      "= matrix_rank:", int(np.linalg.matrix_rank(B)))
# Ehtoluku on suurimman ja pienimmän singulaariarvon suhde.
print(f"ehtoluku s1/s2 = {s[0] / s[1]:.4f},",
      f"np.linalg.cond = {np.linalg.cond(A):.4f}")
# @loppu aste

# @alku pca
# Pääkomponentit suoraan keskitetyn datan hajotelmasta: oikeat
# singulaarivektorit ovat pääsuunnat ja s^2/(m-1) varianssit.
rng = np.random.default_rng(7)
t = rng.uniform(-1.0, 1.0, 500)
suunta = np.array([np.cos(np.radians(30)), np.sin(np.radians(30))])
data = np.outer(t * 3.0, suunta) + rng.normal(0.0, 0.3, (500, 2))
keskitetty = data - data.mean(axis=0)
_, sd, Vd = np.linalg.svd(keskitetty, full_matrices=False)
paa = Vd[0] * np.sign(Vd[0, 0])
print(f"pääsuunta {np.degrees(np.arctan2(paa[1], paa[0])):.1f}°,",
      f"selittää {sd[0]**2 / np.sum(sd**2):.1%} varianssista")
C = keskitetty.T @ keskitetty / (len(data) - 1)
print("s^2/(m-1) = kovarianssimatriisin ominaisarvot:",
      bool(np.allclose(sd[::-1]**2 / (len(data) - 1),
                       np.linalg.eigvalsh(C))))
# @loppu pca
