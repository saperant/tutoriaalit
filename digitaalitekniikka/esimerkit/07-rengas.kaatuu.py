"""Kombinatorinen silmukka: kolmen invertterin rengas.

Parittoman määrän inverttereitä rengas ei voi asettua mihinkään
tilaan, vaan se värähtelee (rengasoskillaattori). Simulaattori
huomaa, ettei tapahtumajono tyhjene, ja keskeyttää.
"""

from porttisim import Piiri

# @alku rengas
piiri = Piiri()
piiri.portti("NOT", ["a"], "b")
piiri.portti("NOT", ["b"], "c")
piiri.portti("NOT", ["c"], "a")      # lähtö takaisin tuloon
piiri.asetu()                         # RuntimeError: värähtelee
# @loppu rengas
print("ei tulostu")
