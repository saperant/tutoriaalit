// Scan-testi laskurille: siirrä tila sisään, yksi toiminnallinen
// jakso (laskuri kasvaa yhdellä), siirrä tulos ulos.
`timescale 1ns/1ps
module tp;
  reg clk = 0, nollaa = 0, sallinta = 1, scan_en = 0, scan_in = 0;
  wire [7:0] q;
  wire scan_out;
  reg [7:0] tila = 8'b1011_0011, ulos;
  integer i;
  laskuri dut (.clk(clk), .nollaa(nollaa), .sallinta(sallinta),
               .q(q), .scan_en(scan_en), .scan_in(scan_in),
               .scan_out(scan_out));
  always #5 clk = ~clk;
  initial if ($test$plusargs("vcd")) begin   // ajoituskaaviota varten
    $dumpfile("scan.vcd"); $dumpvars(0, tp);
  end
  initial begin
    scan_en = 1;                          // siirto: MSB ensin q[7]:ään
    for (i = 7; i >= 0; i = i - 1) begin
      scan_in = tila[i];
      @(posedge clk); #1;
    end
    scan_en = 0;                          // toiminnallinen jakso
    @(posedge clk); #1;
    scan_en = 1;                          // siirto ulos
    for (i = 7; i >= 0; i = i - 1) begin
      ulos[i] = scan_out;
      @(posedge clk); #1;
    end
    $display("sisään %b, ulos %b, odotettu %b", tila, ulos, tila + 8'd1);
    $finish;
  end
endmodule
