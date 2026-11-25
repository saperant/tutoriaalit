"""Kuvan pikselit: uint8-kierto ja kanavien järjestys."""

import numpy as np

# 2 x 3 -kuva, kanavat viimeisenä (korkeus, leveys, RGB) eli HWC.
kuva = np.array([[[250, 10, 0], [128, 128, 128], [0, 0, 255]],
                 [[255, 255, 255], [5, 200, 90], [64, 32, 16]]],
                dtype=np.uint8)

# @alku kirkastus
vaara = kuva + 10                          # uint8 kiertää: 250 -> 4
oikea = np.clip(kuva.astype(np.int16) + 10, 0, 255).astype(np.uint8)
print(vaara[0, 0], oikea[0, 0])
# @loppu kirkastus
# @alku kanavat
chw = kuva.transpose(2, 0, 1)              # kanavat ensin (CHW)
print(kuva.strides, chw.strides, chw.flags["C_CONTIGUOUS"])
print(chw[0])                              # punainen kanava
harmaa = (kuva @ np.array([0.299, 0.587, 0.114])).round().astype(np.uint8)
print(harmaa)
# @loppu kanavat
