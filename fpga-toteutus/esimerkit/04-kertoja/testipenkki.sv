// Testipenkki: kaikki 65 536 tuloa tarkistetaan.
module testipenkki;
  logic        clk = 1'b0;
  logic        kaynnissa = 1'b1;
  logic [7:0]  a = '0, b = '0;
  logic [15:0] tulo;
  int          virheet = 0;

  kertoja dut (.clk, .a, .b, .tulo);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    // @alku tarkistus
    for (int i = 0; i < 256; i++) begin
      for (int j = 0; j < 256; j++) begin
        a = 8'(i);
        b = 8'(j);
        @(posedge clk); #1;
        if (tulo != 16'(i * j)) virheet++;
      end
    end
    // @loppu tarkistus
    $display("tarkistettu 65536 tuloa, virheitä %0d", virheet);
    if (virheet != 0) $fatal(1, "kertoja laskee väärin");
    kaynnissa = 1'b0;
  end
endmodule
