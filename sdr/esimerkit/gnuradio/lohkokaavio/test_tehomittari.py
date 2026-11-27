"""Tehomittarilohkon yksikkotesti GNU Radion omalla tavalla: lahteena
vektori, nieluna vektori, ja lohkokaavio ajetaan loppuun."""

import sys
from pathlib import Path

import numpy as np
from gnuradio import blocks, gr, gr_unittest

from tehomittari_gr import Tehomittari

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "09-lohko"))
from tehomittari import TehoMittari  # noqa: E402


# @alku testi
class TehomittariTesti(gr_unittest.TestCase):
    def setUp(self):
        self.tb = gr.top_block()
        rng = np.random.default_rng(14)
        taso = np.repeat([0.01, 0.1, 0.03], 4000)
        self.signaali = (taso * (rng.standard_normal(len(taso))
                                 + 1j * rng.standard_normal(len(taso)))
                         ).astype(np.complex64)

    def tearDown(self):
        self.tb = None

    def aja(self, signaali):
        lahde = blocks.vector_source_c(signaali.tolist(), False)
        nielu = blocks.vector_sink_f()
        # Python-lohkoon on pidettava viite: connect ei pida oliota
        # elossa, ja roskienkeruun jalkeen ajastin kutsuisi tyhjaa.
        self.lohko = Tehomittari(100)
        self.tb.connect(lahde, self.lohko, nielu)
        self.tb.run()
        return np.array(nielu.data(), dtype=np.float32)

    def test_sama_kuin_logiikka_yksinaan(self):
        """Ajastin valitsee palojen koot; tuloksen on silti oltava
        bitilleen sama kuin logiikalla, joka saa kaiken kerralla."""
        gr_tulos = self.aja(self.signaali)
        lahto = np.empty(len(self.signaali) // 100, dtype=np.float32)
        TehoMittari(100).work([self.signaali], [lahto])
        self.assertEqual(len(gr_tulos), 120)
        self.assertTrue(np.array_equal(gr_tulos, lahto))

    def test_vajaa_loppu_jaa_pois(self):
        """Desimoiva lohko tuottaa lahdon vain taysista sadan paloista."""
        self.assertEqual(len(self.aja(self.signaali[:1050])), 10)
# @loppu testi


if __name__ == "__main__":
    gr_unittest.run(TehomittariTesti)
