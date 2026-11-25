// Monisyklilupauksen tarkistus simuloimalla: kun tulo latautuu, a_r:n
// ja b_r:n edellisestä muutoksesta on oltava vähintään kaksi jaksoa.
// @alku lupaus
`timescale 1ns/1ps
module tp;
  reg clk = 0, nollaa = 1;
  reg [7:0] a = 0, b = 0;
  wire [15:0] tulo;
  kertoja2 dut (.clk(clk), .nollaa(nollaa), .a(a), .b(b), .tulo(tulo));
  always #5 clk = ~clk;
  integer reuna = 0, muuttui = 0, lyhin = 99, latauksia = 0, siemen = 1;
  reg [15:0] ed_tulo, ed_tulot;
  always @(negedge clk) begin a = $random(siemen); b = $random(siemen); end
  always @(posedge clk) begin
    #1 reuna = reuna + 1;
    if (tulo !== ed_tulo && ^ed_tulo !== 1'bx) begin   // tulo latautui
      latauksia = latauksia + 1;
      if (reuna - muuttui < lyhin) lyhin = reuna - muuttui;
    end
    if ({dut.a_r, dut.b_r} !== ed_tulot) muuttui = reuna;
    ed_tulo = tulo;
    ed_tulot = {dut.a_r, dut.b_r};
  end
  initial begin
    repeat (2) @(posedge clk);
    #2 nollaa = 0;
    repeat (40) @(posedge clk);
    $display("tulo latautui %0d kertaa, lyhin aika tulojen muutoksesta %0d jaksoa",
             latauksia, lyhin);
    $finish;
  end
endmodule
// @loppu lupaus
