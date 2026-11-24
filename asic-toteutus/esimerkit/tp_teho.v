// Aktiivisuussimulointi tehoarviota varten: 1000 kellojaksoa,
// sallinta päällä noin neljäsosan ajasta. Kaikki johtimet VCD:hen.
`timescale 1ns/1ps
module tp;
  reg clk = 0, nollaa = 1, sallinta = 0;
  wire [7:0] q;
  integer i, siemen = 3;
  laskuri dut (.clk(clk), .nollaa(nollaa), .sallinta(sallinta), .q(q));
  always #5 clk = ~clk;                    // 100 MHz
  initial begin
    $dumpfile("aktiivisuus.vcd");
    $dumpvars(1, dut);              // vain laskurin johtimet
    @(negedge clk) nollaa = 0;
    for (i = 0; i < 1000; i = i + 1) begin
      sallinta = ($random(siemen) & 3) == 0;
      @(negedge clk);
    end
    $finish;
  end
endmodule
