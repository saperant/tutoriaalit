// @alku kertoja
// Rekisteröity 8 x 8 bitin kertoja. Synteesi päättää, toteutetaanko
// kertolasku DSP-lohkolla vai logiikkasoluilla.
module kertoja (
  input  logic        clk,
  input  logic [7:0]  a,
  input  logic [7:0]  b,
  output logic [15:0] tulo
);
  always_ff @(posedge clk) tulo <= a * b;
endmodule
// @loppu kertoja
