// Skid-puskuri katkaisee valmis-signaalin kombinatorisen polun:
// tuottajalle näkyvä s_valmis tulee suoraan kiikusta. Kun kuluttaja
// pysähtyy, tuottaja kuulee siitä vasta seuraavalla jaksolla, ja sillä
// välin lähetetty sana otetaan talteen varapaikkaan.
module skid_puskuri #(
  parameter int W = 8
) (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         s_kelv,
  output logic         s_valmis,
  input  logic [W-1:0] s_data,
  output logic         u_kelv,
  input  logic         u_valmis,
  output logic [W-1:0] u_data
);
  // @alku skid
  logic         vara_kelv;           // varapaikassa on sana
  logic [W-1:0] vara;

  assign s_valmis = !vara_kelv;                  // suoraan kiikusta
  assign u_kelv   = vara_kelv || s_kelv;
  assign u_data   = vara_kelv ? vara : s_data;   // vanhin sana ensin

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)                             vara_kelv <= 1'b0;
    else if (u_valmis)                      vara_kelv <= 1'b0;
    else if (s_kelv && s_valmis)            vara_kelv <= 1'b1;
  end

  always_ff @(posedge clk) begin
    if (s_kelv && s_valmis && !u_valmis) vara <= s_data;
  end
  // @loppu skid
endmodule
