// Asynkroninen FIFO: kirjoitus ja luku eri kelloilla. Osoittimet
// ylittävät rajan Gray-koodattuina: peräkkäiset arvot eroavat vain
// yhdellä bitillä, joten tahdistettu arvo on aina joko vanha tai uusi
// osoitin, ei koskaan bittien sekoitus.
module asynk_fifo #(
  parameter int W  = 8,
  parameter int AW = 4                // syvyys 2**AW
) (
  input  logic         k_clk, k_rst_n,
  input  logic         kirjoita,
  input  logic [W-1:0] k_data,
  output logic         taynna,
  input  logic         l_clk, l_rst_n,
  input  logic         lue,
  output logic [W-1:0] l_data,
  output logic         tyhja
);
  // @alku gray
  function automatic logic [AW:0] gray(logic [AW:0] b);
    return b ^ (b >> 1);
  endfunction
  // @loppu gray

  logic [W-1:0] muisti [2**AW];
  logic [AW:0]  k_bin, k_gray, l_bin, l_gray;   // omat osoittimet
  logic [AW:0]  l_gray_k, k_gray_l;             // tahdistetut
  logic [AW:0]  k_bin_seur, l_bin_seur;

  // @alku kirjoitus
  // Kirjoituspuoli: täynnä, kun lukuosoitin on tasan kierroksen jäljessä.
  // Gray-koodissa se tarkoittaa: kaksi ylintä bittiä eri, muut samat.
  assign k_bin_seur = k_bin + (AW+1)'(kirjoita && !taynna);

  always_ff @(posedge k_clk or negedge k_rst_n) begin
    if (!k_rst_n) begin
      {k_bin, k_gray, taynna} <= '0;
    end else begin
      k_bin  <= k_bin_seur;
      k_gray <= gray(k_bin_seur);
      taynna <= gray(k_bin_seur) ==
                {~l_gray_k[AW:AW-1], l_gray_k[AW-2:0]};
    end
  end

  always_ff @(posedge k_clk)
    if (kirjoita && !taynna) muisti[k_bin[AW-1:0]] <= k_data;
  // @loppu kirjoitus

  // @alku luku
  // Lukupuoli: tyhjä, kun osoittimet ovat samat.
  assign l_bin_seur = l_bin + (AW+1)'(lue && !tyhja);

  always_ff @(posedge l_clk or negedge l_rst_n) begin
    if (!l_rst_n) begin
      {l_bin, l_gray} <= '0;
      tyhja           <= 1'b1;
    end else begin
      l_bin  <= l_bin_seur;
      l_gray <= gray(l_bin_seur);
      tyhja  <= gray(l_bin_seur) == k_gray_l;
    end
  end
  assign l_data = muisti[l_bin[AW-1:0]];
  // @loppu luku

  // @alku tahdistus
  // Vain rekistereistä lähtevät Gray-osoittimet ylittävät rajan.
  logic [AW:0] l_gray_m, k_gray_m;
  always_ff @(posedge k_clk or negedge k_rst_n)
    if (!k_rst_n) {l_gray_k, l_gray_m} <= '0;
    else          {l_gray_k, l_gray_m} <= {l_gray_m, l_gray};

  always_ff @(posedge l_clk or negedge l_rst_n)
    if (!l_rst_n) {k_gray_l, k_gray_m} <= '0;
    else          {k_gray_l, k_gray_m} <= {k_gray_m, k_gray};
  // @loppu tahdistus
endmodule
