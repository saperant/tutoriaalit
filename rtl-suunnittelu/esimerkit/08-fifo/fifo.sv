// Synkroninen FIFO. Osoittimissa on yksi ylimääräinen bitti, jolla
// täysi ja tyhjä erotetaan toisistaan ilman erillistä laskuria.
// Luettava sana näkyy ulostulossa jo ennen lukua (first-word fall-
// through), joten lue toimii kuittauksena.
module fifo #(
  parameter int W = 8,
  parameter int SYVYYS = 16           // kahden potenssi
) (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         kirjoita,
  input  logic [W-1:0] k_data,
  output logic         taynna,
  input  logic         lue,
  output logic [W-1:0] l_data,
  output logic         tyhja
);
  localparam int AW = $clog2(SYVYYS);
  if (SYVYYS != (1 << AW)) begin : g_tarkistus
    $error("fifo: SYVYYS=%0d ei ole kahden potenssi", SYVYYS);
  end

  // @alku osoittimet
  logic [W-1:0] muisti [SYVYYS];
  logic [AW:0]  k_os, l_os;           // AW+1 bittiä

  assign tyhja  = (k_os == l_os);
  assign taynna = (k_os[AW] != l_os[AW]) &&
                  (k_os[AW-1:0] == l_os[AW-1:0]);
  assign l_data = muisti[l_os[AW-1:0]];

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      k_os <= '0;
      l_os <= '0;
    end else begin
      if (kirjoita && !taynna) k_os <= k_os + 1'b1;
      if (lue && !tyhja)       l_os <= l_os + 1'b1;
    end
  end

  always_ff @(posedge clk)
    if (kirjoita && !taynna) muisti[k_os[AW-1:0]] <= k_data;
  // @loppu osoittimet
endmodule
