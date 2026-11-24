// @alku vilkku
// Vilkuttaa lediä: laskuri jakaa kellotaajuuden, ja laskurin ylin
// bitti ohjaa lediä. iCEBreaker-kortin ledit palavat, kun nasta on 0.
module vilkku #(
  parameter int BITIT = 24    // 12 MHz / 2^24 ≈ 0,7 Hz
) (
  input  logic clk,
  output logic led_n
);
  // FPGA:n kiikut saavat alkuarvon konfiguroinnissa, joten pelkkä
  // laskuri ei tarvitse nollausta.
  logic [BITIT-1:0] laskuri = '0;

  always_ff @(posedge clk) laskuri <= laskuri + 1'b1;

  assign led_n = ~laskuri[BITIT-1];
endmodule
// @loppu vilkku
