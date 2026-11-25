// Liukuhihnan vaihe kelvollinen/valmis-kättelyllä. Vaihe ottaa uuden
// sanan, kun se on tyhjä tai kuluttaja vie nykyisen sanan samalla
// jaksolla. Kun kuluttaja ei ole valmis, data ja kelvollisuus pysyvät.
module kattelyvaihe #(
  parameter int W = 8
) (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         s_kelv,       // sisään: tuottajalta
  output logic         s_valmis,
  input  logic [W-1:0] s_data,
  output logic         u_kelv,       // ulos: kuluttajalle
  input  logic         u_valmis,
  output logic [W-1:0] u_data
);
  // @alku vaihe
  // Kombinatorinen polku: u_valmis kulkee vaiheen läpi tuottajalle.
  assign s_valmis = !u_kelv || u_valmis;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)        u_kelv <= 1'b0;
    else if (s_valmis) u_kelv <= s_kelv;
  end

  always_ff @(posedge clk) begin
    if (s_valmis && s_kelv) u_data <= s_data;
  end
  // @loppu vaihe
endmodule
