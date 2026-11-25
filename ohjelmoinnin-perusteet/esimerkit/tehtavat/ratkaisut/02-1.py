"""Malliratkaisu 02-1: Munakennot."""

KENNON_KOKO = 12

munia = int(input())
kennoja = munia // KENNON_KOKO
yli = munia % KENNON_KOKO
print(f"Kennoja: {kennoja}, yli: {yli}")
