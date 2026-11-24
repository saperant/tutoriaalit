// Rekisteröity 8×8-bittinen kertoja: tulorekisterit, kombinatorinen
// kertolasku ja tulosrekisteri.
// @alku kertoja
module kertoja (
  input  wire        clk,
  input  wire [7:0]  a,
  input  wire [7:0]  b,
  output reg  [15:0] tulo
);
  reg [7:0] a_r, b_r;
  always @(posedge clk) begin
    a_r  <= a;
    b_r  <= b;
    tulo <= a_r * b_r;
  end
endmodule
// @loppu kertoja
