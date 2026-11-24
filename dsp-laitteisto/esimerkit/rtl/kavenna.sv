// @alku kavenna
// Leveä summa kapeaksi ulostuloksi: alimmat SIIRTO bittiä pyöristetään
// pois (lähimpään, puolikkaat ylöspäin) ja tulos saturoidaan OW
// bittiin. Vastaa mallin funktiota malli.kiintea.ulostulo().
module kavenna #(
  parameter int IW     = 32,   // sisääntulon leveys
  parameter int OW     = 12,   // ulostulon leveys
  parameter int SIIRTO = 15    // pudotettavat bitit, vähintään 2
) (
  input  logic signed [IW-1:0] a,
  output logic signed [OW-1:0] y
);
  localparam int SW = IW + 1 - SIIRTO;   // pyöristetyn leveys

  // Pyöristys: puolikas lisätään ennen katkaisua. Summa levennetään
  // bitillä, jotta suurinkaan sisääntulo ei vuoda yli.
  // Pudotettavat alimmat bitit jäävät tarkoituksella käyttämättä.
  /* verilator lint_off UNUSEDSIGNAL */
  logic signed [IW:0] puolikas, summa;
  /* verilator lint_on UNUSEDSIGNAL */
  assign puolikas = {{(IW + 1 - SIIRTO){1'b0}}, 1'b1, {(SIIRTO - 1){1'b0}}};
`ifdef BUGI_KATKAISU
  assign summa = {a[IW-1], a};            // vika: puolikas unohtui
`else
  assign summa = {a[IW-1], a} + puolikas;
`endif

  // Alimmat bitit pudotetaan pelkällä johdotuksella.
  logic signed [SW-1:0] lyhyt;
  assign lyhyt = summa[IW:SIIRTO];

  // Saturaatio: arvo mahtuu OW bittiin, jos pudotettavat ylimmät bitit
  // ja uuden etumerkkibitin paikka ovat kaikki samoja.
  logic mahtuu;
  assign mahtuu = &lyhyt[SW-1:OW-1] || ~|lyhyt[SW-1:OW-1];
`ifdef BUGI_KIERTO
  assign y = lyhyt[OW-1:0];               // vika: ylivuoto kiertää
`else
  assign y = mahtuu   ? lyhyt[OW-1:0]
           : lyhyt[SW-1] ? {1'b1, {(OW - 1){1'b0}}}    // pienin
           :               {1'b0, {(OW - 1){1'b1}}};   // suurin
`endif
endmodule
// @loppu kavenna
