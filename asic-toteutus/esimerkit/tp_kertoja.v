// Testipenkki, joka ajetaan sekä RTL:lle että porttitason netlistalle.
// Tulosteet vertaillaan: niiden on oltava samat.
`timescale 1ns/1ps
module tp;
  reg clk = 0;
  reg [7:0] a = 0, b = 0;
  wire [15:0] tulo;
  integer i, siemen = 7;
  kertoja dut (.clk(clk), .a(a), .b(b), .tulo(tulo));
  always #5 clk = ~clk;
  initial begin
    for (i = 0; i < 200; i = i + 1) begin
      @(negedge clk);
      a = $random(siemen);
      b = $random(siemen);
      if (i >= 2) $display("%0d %0d", i, tulo);
    end
    $finish;
  end
endmodule
