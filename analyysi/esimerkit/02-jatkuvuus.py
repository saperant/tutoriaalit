"""Jatkuvuus: toispuoleiset raja-arvot ja poistuva epäjatkuvuus."""

import sympy as sp

x = sp.symbols("x", real=True)


# @alku jatkuva
def jatkuva_kohdassa(vasen: sp.Expr, oikea: sp.Expr, arvo: sp.Expr,
                     a: sp.Expr) -> bool:
    """Paloittain määritelty funktio on jatkuva rajakohdassa a, jos
    vasemman palan raja-arvo vasemmalta, oikean palan raja-arvo
    oikealta ja funktion arvo ovat sama äärellinen luku."""
    rv = sp.limit(vasen, x, a, "-")
    ro = sp.limit(oikea, x, a, "+")
    print(f"  vasemmalta {rv}, oikealta {ro}, arvo {arvo}")
    return bool(rv == ro == arvo and arvo.is_finite)


# Lämmityksen teho (W) lämpötilan x (C) funktiona: teho pienenee
# lineaarisesti ja on nolla 20 asteesta ylöspäin.
print("teho:", jatkuva_kohdassa(100 - 5 * x, sp.Integer(0),
                                sp.Integer(0), sp.Integer(20)))
# Kirjoitusvirhe: oikealla palalla 10 W.
print("virhe:", jatkuva_kohdassa(100 - 5 * x, sp.Integer(10),
                                 sp.Integer(10), sp.Integer(20)))
# @loppu jatkuva

# @alku poistuva
# sin(x)/x ei ole määritelty nollassa, mutta raja-arvo on 1:
# epäjatkuvuus poistuu, kun arvoksi määritellään 1 (sinc-funktio).
sinc = sp.sin(x) / x
print("sin(x)/x nollassa:", sinc.subs(x, 0))
print("sinc:", jatkuva_kohdassa(sinc, sinc, sp.Integer(1), sp.Integer(0)))
# @loppu poistuva
