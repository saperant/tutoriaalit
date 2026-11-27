"""Luvun 5 FM-monovastaanotin GNU Radion lohkokaaviona.

Kaytto: gr-python fm_mono.py TALLENNE.cu8 AANI.f32 TASO.f32

Lahteena on tiedosto ja nieluina tiedostot, joten kaavio ajetaan
loppuun ilman radiota, aanikorttia ja nayttoa.
"""

import math
import sys

from gnuradio import analog, blocks, gr
from gnuradio import filter as suotimet
from gnuradio.filter import firdes

from tehomittari_gr import Tehomittari

FS_IQ = 912_000.0          # tallenteen naytetaajuus
FS_MPX = 228_000.0         # kanavasuotimen jalkeen
FS_AANI = 48_000.0
ASEMA_HZ = 200e3           # aseman paikka tallenteessa
POIKKEAMA = 75_000.0


# @alku lahde
class Cu8Lahde(gr.hier_block2):
    """RTL-SDR:n cu8-tiedosto kompleksinaytteiksi valille -1...1."""

    def __init__(self, polku):
        gr.hier_block2.__init__(
            self, "Cu8Lahde", gr.io_signature(0, 0, 0),
            gr.io_signature(1, 1, gr.sizeof_gr_complex))
        tiedosto = blocks.file_source(gr.sizeof_char, polku, False)
        liukuluvuksi = blocks.uchar_to_float()
        nolla = blocks.add_const_ff(-127.5)
        skaala = blocks.multiply_const_ff(1 / 127.5)
        erota = blocks.deinterleave(gr.sizeof_float)     # I, Q, I, Q, ...
        kompleksiksi = blocks.float_to_complex()
        self.connect(tiedosto, liukuluvuksi, nolla, skaala, erota)
        self.connect((erota, 0), (kompleksiksi, 0))
        self.connect((erota, 1), (kompleksiksi, 1))
        self.connect(kompleksiksi, self)
# @loppu lahde


# @alku kaavio
class FmMono(gr.top_block):
    def __init__(self, tallenne, aani, taso):
        gr.top_block.__init__(self, "FM-monovastaanotin")
        lahde = Cu8Lahde(tallenne)
        # Siirto nollaan, 100 kHz:n alipaasto ja desimointi neljalla.
        kanava = suotimet.freq_xlating_fir_filter_ccc(
            4, firdes.low_pass(1.0, FS_IQ, 100e3, 20e3), ASEMA_HZ, FS_IQ)
        # Lahto on 1, kun taajuus poikkeaa huippupoikkeaman verran.
        ilmaisin = analog.quadrature_demod_cf(
            FS_MPX / (2 * math.pi * POIKKEAMA))
        jalkikorostus = analog.fm_deemph(FS_MPX, 50e-6)
        # 15 kHz:n alipaasto poistaa pilotin ja kaiken sen ylapuolelta;
        # samalla 228 kHz -> 48 kHz (4/19).
        aaneksi = suotimet.rational_resampler_fff(
            4, 19, firdes.low_pass(4.0, 4 * FS_MPX, 15e3, 4e3))
        aaninielu = blocks.file_sink(gr.sizeof_float, aani, False)
        # Oma lohko haarautuu kanavasuotimen lahdosta: 100 arvoa/s.
        self.mittari = Tehomittari(2280)
        tasonielu = blocks.file_sink(gr.sizeof_float, taso, False)
        self.connect(lahde, kanava, ilmaisin, jalkikorostus, aaneksi,
                     aaninielu)
        self.connect(kanava, self.mittari, tasonielu)
# @loppu kaavio


# @alku aja
if __name__ == "__main__":
    FmMono(*sys.argv[1:4]).run()      # palaa, kun tiedosto on luettu
# @loppu aja
