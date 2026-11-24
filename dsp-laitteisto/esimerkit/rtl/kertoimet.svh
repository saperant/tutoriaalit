// GENEROITU: python3 -m malli.generoi. Älä muokkaa käsin.
// Kertoimet pakattuina vakioina, alkio 0 alimpina bitteinä.
`ifndef KERTOIMET_SVH
`define KERTOIMET_SVH

`define FIR_KERTOIMET { \
  16'hff57, 16'hfd12, 16'h0c62, 16'h3735, \
  16'h3735, 16'h0c62, 16'hfd12, 16'hff57 \
}

`define POLYFAASI_KERTOIMET { \
  16'hffd6, 16'hff4f, 16'hfe6a, 16'hfea0, \
  16'h029d, 16'h0b91, 16'h16d6, 16'h1ecd, \
  16'h1ecd, 16'h16d6, 16'h0b91, 16'h029d, \
  16'hfea0, 16'hfe6a, 16'hff4f, 16'hffd6 \
}

`define SOS0_KERTOIMET {16'h2393, 16'ha14d, 16'h0138, 16'h0270, 16'h0138}
`define SOS1_KERTOIMET {16'h3277, 16'h9323, 16'h0167, 16'h02cd, 16'h0167}

`endif
