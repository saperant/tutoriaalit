// Kirjoitus 100 MHz:llä ja luku noin 37 MHz:llä. Lähetetään 300
// peräkkäistä tavua ja tarkistetaan, että ne tulevat järjestyksessä.
module testipenkki;
  logic       k_clk = 1'b0, l_clk = 1'b0, kaynnissa = 1'b1;
  logic       rst_n = 1'b0;
  logic       kirjoita = 1'b0, lue = 1'b0, taynna, tyhja;
  logic [7:0] k_data = '0, l_data, odotettu = '0;
  int         luettu = 0, virheita = 0, taynna_jaksoja = 0;

  asynk_fifo #(.W(8), .AW(3)) u_f (
    .k_clk, .k_rst_n(rst_n), .kirjoita, .k_data, .taynna,
    .l_clk, .l_rst_n(rst_n), .lue, .l_data, .tyhja);

  initial while (kaynnissa) #5  k_clk = ~k_clk;
  initial while (kaynnissa) #13 l_clk = ~l_clk;

  // Kuluttaja lukee aina kun voi ja tarkistaa järjestyksen.
  always @(posedge l_clk) begin
    if (lue && !tyhja) begin
      if (l_data != odotettu) virheita <= virheita + 1;
      odotettu <= odotettu + 1'b1;
      luettu   <= luettu + 1;
    end
  end
  always @(posedge k_clk) if (taynna) taynna_jaksoja <= taynna_jaksoja + 1;

  initial begin
    #30 rst_n = 1'b1;
    lue = 1'b1;
    @(posedge k_clk); #1;
    for (int i = 0; i < 300; i++) begin
      kirjoita = 1'b1;
      k_data   = 8'(i);
      do @(posedge k_clk); while (taynna);   // odota tilaa
      #1;
    end
    kirjoita = 1'b0;
    wait (luettu == 300);
    #1;
    $display("luettu %0d tavua, virheitä %0d", luettu, virheita);
    $display("kirjoittaja odotti täyttä jonoa: %s",
             taynna_jaksoja > 0 ? "kyllä" : "ei");
    if (virheita != 0) $fatal(1, "asynkroninen FIFO väärin");
    kaynnissa = 1'b0;
  end
endmodule
