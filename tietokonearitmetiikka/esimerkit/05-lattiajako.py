"""Pythonin // ja % pyöristävät kohti miinus ääretöntä."""

import math

# @alku python
print(7 // 2, 7 % 2, -7 // 2, -7 % 2, 7 // -2, 7 % -2)
print(int(-7 / 2), math.fmod(-7, 2))        # C:n kaltainen katkaisu
print(divmod(15 - 45, 24 * 60))             # (päivä, minuutti)
print(-(-101 // 25))                        # kattojako
# @loppu python
