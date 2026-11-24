// Asynkroninen FIFO kahden kellotusalueen välille (Grayn koodatut
// osoittimet, kaksikiikkuiset tahdistimet). Rakenne on sama kuin
// RTL-suunnittelun luvussa Kellotusalueiden ylitys.
// @alku liitanta
module async_fifo #(
  parameter int LEVEYS = 8,
  parameter int OSOITE = 4            // syvyys 2^OSOITE
) (
  // kirjoituspuoli, kello clk_k
  input  logic              clk_k,
  input  logic              kirjoita,
  input  logic [LEVEYS-1:0] tieto_sisaan,
  output logic              tayna,
  // lukupuoli, kello clk_l
  input  logic              clk_l,
  input  logic              lue,
  output logic [LEVEYS-1:0] tieto_ulos,
  output logic              tyhja
);
// @loppu liitanta
  localparam int SYVYYS = 1 << OSOITE;
  logic [LEVEYS-1:0] muisti [SYVYYS];

  logic [OSOITE:0] k_bin = '0, k_gray = '0, l_bin = '0, l_gray = '0;
  logic [OSOITE:0] l_gray_k1 = '0, l_gray_k2 = '0;   // lukuosoitin -> k
  logic [OSOITE:0] k_gray_l1 = '0, k_gray_l2 = '0;   // kirj.osoitin -> l

  function automatic logic [OSOITE:0] gray(input logic [OSOITE:0] b);
    gray = b ^ (b >> 1);
  endfunction

  // Kirjoituspuoli
  logic [OSOITE:0] k_bin_seur;
  assign k_bin_seur = k_bin + (OSOITE + 1)'(kirjoita && !tayna);
  always_ff @(posedge clk_k) begin
    if (kirjoita && !tayna) muisti[k_bin[OSOITE-1:0]] <= tieto_sisaan;
    k_bin  <= k_bin_seur;
    k_gray <= gray(k_bin_seur);
    {l_gray_k2, l_gray_k1} <= {l_gray_k1, l_gray};
  end
  // Täynnä: ylimmät kaksi bittiä eroavat, muut samat (Gray-vertailu).
  assign tayna = k_gray == {~l_gray_k2[OSOITE:OSOITE-1],
                            l_gray_k2[OSOITE-2:0]};

  // Lukupuoli
  logic [OSOITE:0] l_bin_seur;
  assign l_bin_seur = l_bin + (OSOITE + 1)'(lue && !tyhja);
  always_ff @(posedge clk_l) begin
    l_bin  <= l_bin_seur;
    l_gray <= gray(l_bin_seur);
    {k_gray_l2, k_gray_l1} <= {k_gray_l1, k_gray};
  end
  assign tyhja = l_gray == k_gray_l2;
  assign tieto_ulos = muisti[l_bin[OSOITE-1:0]];
endmodule
