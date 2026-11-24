"""Sarjat: osasummat, suppeneminen ja potenssisarjan suppenemissäde."""

import math

import sympy as sp

k, x = sp.symbols("k x")
n = sp.symbols("n", positive=True, integer=True)

# @alku osasummat
# Geometrinen sarja sum q^k suppenee, kun |q| < 1: summa 1/(1 - q).
print("sum (1/2)^k, k=0..oo =", sp.summation(sp.Rational(1, 2) ** k,
                                              (k, 0, sp.oo)))
# Harmoninen sarja hajaantuu, vaikka termit pienenevät nollaan.
print("sum 1/k =", sp.summation(1 / k, (k, 1, sp.oo)))
print("sum 1/k^2 =", sp.summation(1 / k**2, (k, 1, sp.oo)))
# Osasumma H(N) kasvaa kuin ln N + 0,5772 (Eulerin vakio).
for m in range(1, 7):
    N = 10**m
    H = math.fsum(1 / j for j in range(1, N + 1))
    arvio = math.log(N) + 0.5772
    print(f"  H(10^{m}) = {H:8.4f}   ln N + 0,5772 = {arvio:8.4f}")
# @loppu osasummat

# @alku suhde
# Suhdetesti: jos |a_{n+1} / a_n| -> L < 1, sarja suppenee.
a = 2**n / sp.factorial(n)
print("suhde 2^n/n!:", sp.limit(sp.simplify(a.subs(n, n + 1) / a), n, sp.oo))
print("sum 2^n/n! =", sp.summation(2**k / sp.factorial(k), (k, 0, sp.oo)))
# Potenssisarja sum x^k / k: suppenemissäde suhdetestistä.
b = 1 / n
print("säde: 1 /", sp.limit(b.subs(n, n + 1) / b, n, sp.oo))
# @loppu suhde
