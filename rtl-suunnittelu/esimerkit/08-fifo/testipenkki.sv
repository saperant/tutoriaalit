// FIFO:n testipenkki: tuottaja ja kuluttaja toimivat näennäis-
// satunnaisesti, ja SystemVerilogin jono on viitemalli.
module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic       kirjoita = 1'b0, lue = 1'b0, taynna, tyhja;
  logic [7:0] k_data = '0, l_data;
  logic [7:0] malli[$];
  logic [15:0] lfsr = 16'h1D0F;
  int         kirjoitettu = 0, luettu = 0, virheita = 0;
  int         taynna_jaksoja = 0, tyhja_jaksoja = 0;

  fifo #(.W(8), .SYVYYS(8)) u_fifo (.clk, .rst_n, .kirjoita, .k_data,
                                    .taynna, .lue, .l_data, .tyhja);

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku malli
  always @(posedge clk) begin
    // Liput kuvaavat reunaa edeltävää tilaa: tarkistus ennen päivitystä.
    if ((malli.size() == 8) != taynna || (malli.size() == 0) != tyhja)
      $fatal(1, "lippu ei vastaa mallia");
    if (kirjoita && !taynna) begin
      malli.push_back(k_data);
      kirjoitettu <= kirjoitettu + 1;
    end
    if (lue && !tyhja) begin
      if (malli.size() == 0 || l_data != malli.pop_front())
        virheita <= virheita + 1;
      luettu <= luettu + 1;
    end
    if (taynna) taynna_jaksoja <= taynna_jaksoja + 1;
    if (tyhja)  tyhja_jaksoja  <= tyhja_jaksoja + 1;
  end
  // @loppu malli

  initial begin
    #12 rst_n = 1'b1;
    // Kolme vaihetta: tuottaja nopeampi, tasainen, kuluttaja nopeampi.
    for (int vaihe = 0; vaihe < 3; vaihe++) begin
      for (int i = 0; i < 200; i++) begin
        lfsr     = {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
        kirjoita = (lfsr[2:0] < 3'(6 - 2 * vaihe));
        lue      = (lfsr[5:3] < 3'(2 + 2 * vaihe));
        k_data   = lfsr[15:8];
        @(posedge clk); #1;
      end
    end
    kirjoita = 1'b0;
    lue      = 1'b1;
    while (!tyhja) begin
      @(posedge clk); #1;
    end
    $display("kirjoitettu %0d, luettu %0d, virheitä %0d", kirjoitettu,
             luettu, virheita);
    $display("täynnä %0d jaksoa, tyhjä %0d jaksoa", taynna_jaksoja,
             tyhja_jaksoja);
    if (virheita != 0 || kirjoitettu != luettu) $fatal(1, "FIFO väärin");
    kaynnissa = 1'b0;
  end
endmodule
