// Testipenkki: kirjoittaja 12 MHz:n kellolla, lukija 48 MHz:n kellolla
// (jaksot 84 ja 20 aikayksikköä). 20 tavua kulkee perille järjestyksessä.
module testipenkki;
  logic       clk_k = 1'b0, clk_l = 1'b0, kaynnissa = 1'b1;
  logic       kirjoita = 1'b0, lue = 1'b0, tayna, tyhja;
  logic [7:0] tieto_sisaan = '0, tieto_ulos;
  int         luettu = 0;

  async_fifo dut (.clk_k, .kirjoita, .tieto_sisaan, .tayna,
                  .clk_l, .lue, .tieto_ulos, .tyhja);

  initial while (kaynnissa) #42 clk_k = ~clk_k;
  initial while (kaynnissa) #10 clk_l = ~clk_l;

  initial begin            // kirjoittaja
    for (int i = 0; i < 20; i++) begin
      @(negedge clk_k);
      while (tayna) @(negedge clk_k);
      kirjoita = 1'b1;
      tieto_sisaan = 8'(100 + i);
      @(negedge clk_k) kirjoita = 1'b0;
    end
  end

  initial begin            // lukija
    while (luettu < 20) begin
      @(negedge clk_l);
      lue = !tyhja;
      if (!tyhja) begin
        if (tieto_ulos != 8'(100 + luettu)) $fatal(1, "järjestys rikki");
        luettu++;
      end
    end
    $display("20 tavua kellotusalueen yli oikeassa järjestyksessä");
    kaynnissa = 1'b0;
  end
endmodule
