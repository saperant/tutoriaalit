"""Tehomittarin kaare GNU Radion lohkoksi.

Kaareessa ei ole signaalinkasittelya: se kertoo GNU Radiolle lohkon
tyypin, porttien tyypit ja desimointisuhteen ja valittaa work-kutsun
logiikalle, joka on testattu ilman GNU Radiota (../../09-lohko).
"""

import sys
from pathlib import Path

import numpy as np
from gnuradio import gr

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "09-lohko"))
from tehomittari import TehoMittari  # noqa: E402


# @alku kaare
class Tehomittari(gr.decim_block):
    """Yksi dBFS-arvo jokaista 'desimointi' tulonaytetta kohti."""

    def __init__(self, desimointi=100, alfa=0.1):
        gr.decim_block.__init__(self, name="Tehomittari",
                                in_sig=[np.complex64],
                                out_sig=[np.float32], decim=desimointi)
        self.logiikka = TehoMittari(desimointi, alfa)

    def work(self, input_items, output_items):
        return self.logiikka.work(input_items, output_items)
# @loppu kaare
