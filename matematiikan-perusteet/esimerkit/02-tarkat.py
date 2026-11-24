"""Tarkat luvut ja liukuluvut: milloin numeerinen tulos harhauttaa."""

import sympy as sp

# @alku liukuluvut
print("0.1 + 0.2 =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)
kolmasosa = sp.Rational(1, 3)
print("1/3 + 1/3 + 1/3 =", kolmasosa * 3)
print("sqrt(2)**2 =", sp.sqrt(2) ** 2, " (float:", 2**0.5 * 2**0.5, ")")
# @loppu liukuluvut

# @alku ansa
x = sp.symbols("x")
vaara = x + 1 / 3                      # Python laskee 1/3 ensin floatiksi
oikein = x + sp.Rational(1, 3)
print("vaara:", vaara, "  oikein:", oikein)
print("S(1)/3:", sp.S(1) / 3, " nsimplify:", sp.nsimplify(0.25))
# @loppu ansa

# @alku tarkkuus
pii = sp.pi
print("pi, 30 numeroa:", pii.evalf(30))
iso = sp.Integer(10) ** 20 + 1
print("10**20 + 1 tarkasti:", iso, " float:", float(iso))
print("float pyöristää:", float(iso) == float(10**20))
# @loppu tarkkuus
