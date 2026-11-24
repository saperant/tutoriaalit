"""SymPyn peruskäyttö: symbolit, muokkaus, sijoitus ja ratkaiseminen."""

import sympy as sp

# @alku symbolit
x, y = sp.symbols("x y")
a = sp.symbols("a", positive=True)     # oletus: a > 0
lauseke = (x + y) ** 2 - (x - y) ** 2
print("lauseke:", lauseke)
print("expand:", sp.expand(lauseke))
print("sqrt(a**2):", sp.sqrt(a**2), " sqrt(x**2):", sp.sqrt(x**2))
# @loppu symbolit

# @alku muokkaus
p = x**3 - 6 * x**2 + 11 * x - 6
print("factor:", sp.factor(p))
q = (x**2 - 1) / (x**2 + 2 * x + 1)
print("cancel:", sp.cancel(q))
r = sp.sin(x) ** 2 + sp.cos(x) ** 2
print("simplify:", sp.simplify(r))
print("collect:", sp.collect(sp.expand((x + 2) * (x + y)), x))
# @loppu muokkaus

# @alku sijoitus
f = x**2 - 3 * x
print("f(4) =", f.subs(x, 4))
print("f(1/3) =", f.subs(x, sp.Rational(1, 3)))
print("f(sqrt(2)) =", sp.expand(f.subs(x, sp.sqrt(2))))
print("likiarvo:", f.subs(x, sp.sqrt(2)).evalf(8))
# @loppu sijoitus

# @alku ratkaisu
print("solve:", sp.solve(x**2 - 5 * x + 6, x))
print("solve, kaksi muuttujaa:",
      sp.solve([x + y - 10, x - y - 2], [x, y], dict=True))
print("solveset R:", sp.solveset(x**2 + 1, x, domain=sp.S.Reals))
print("solveset C:", sp.solveset(x**2 + 1, x, domain=sp.S.Complexes))
# @loppu ratkaisu

# @alku numeeriseksi
g = sp.lambdify(x, sp.exp(-x) * sp.sin(x), modules="math")
print("g(1) =", round(g(1.0), 6))
print("nsolve:", sp.nsolve(sp.cos(x) - x, x, 0.5))
# @loppu numeeriseksi
