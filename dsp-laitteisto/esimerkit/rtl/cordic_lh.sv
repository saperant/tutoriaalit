// @alku liitanta
// Liukuhihnoitettu CORDIC: esikierto ja jokainen kierros omana
// vaiheenaan. Uusi syöte joka jaksolla, latenssi KIERROKSET + 1.
// s_tila 0 = rotaatio (kierrä (x, y) kulmalla z), 1 = vektori (kierrä
// (x, y) x-akselille ja kerää kulma z:aan). Sisääntulot Q1.15 ja
// 16-bittinen kulma (täysi kierros 2**16); ulostulot sisäisessä
// muodossa: x ja y Q3.17 (CORDICin vahvistus mukana), z 18 bittiä.
module cordic_lh #(
  parameter int KIERROKSET = 16,
  parameter int XW = 20,
  parameter int ZW = 18
) (
  input  logic                 clk,
  input  logic                 nollaus,
  input  logic                 s_valid,
  output logic                 s_ready,
  input  logic                 s_tila,
  input  logic signed [15:0]   s_x,
  input  logic signed [15:0]   s_y,
  input  logic signed [15:0]   s_z,
  output logic                 m_valid,
  input  logic                 m_ready,
  output logic signed [XW-1:0] m_x,
  output logic signed [XW-1:0] m_y,
  output logic signed [ZW-1:0] m_z
);
  // @loppu liitanta
  `include "cordic_kulmat.svh"

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  // @alku esikierto
  // Esikierto: Q1.15 -> Q3.17 ja 16 -> 18 bittiä. Jos kulma ei ole
  // CORDICin suppenemisalueella (rotaatio: 2. tai 3. neljännes;
  // vektori: x < 0), vektori käännetään ja kulmaan lisätään pii.
  logic signed [XW-1:0] xs, ys;
  logic signed [ZW-1:0] zs;
  logic                 kaanna;
  assign xs = {{(XW - 18){s_x[15]}}, s_x, 2'b00};
  assign ys = {{(XW - 18){s_y[15]}}, s_y, 2'b00};
  assign zs = {s_z, 2'b00};
  assign kaanna = s_tila ? s_x[15] : s_z[15] ^ s_z[14];
  // @loppu esikierto

  // @alku vaiheet
  logic signed [XW-1:0] x [KIERROKSET+1];
  logic signed [XW-1:0] y [KIERROKSET+1];
  logic signed [ZW-1:0] z [KIERROKSET+1];
  logic                 tila [KIERROKSET+1];
  logic                 v [KIERROKSET+1];

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i <= KIERROKSET; i++) v[i] <= 1'b0;
    end else if (eteen) begin
      v[0]    <= s_valid;
      tila[0] <= s_tila;
      x[0]    <= kaanna ? -xs : xs;
      y[0]    <= kaanna ? -ys : ys;
      z[0]    <= kaanna ? zs + ZW'(1 << (ZW - 1)) : zs;
      for (int i = 0; i < KIERROKSET; i++) begin
        v[i+1]    <= v[i];
        tila[i+1] <= tila[i];
        // Kiertosuunta: rotaatiossa kohti z = 0, vektorissa kohti y = 0.
        if (tila[i] ? y[i][XW-1] : !z[i][ZW-1]) begin
          x[i+1] <= x[i] - (y[i] >>> i);
          y[i+1] <= y[i] + (x[i] >>> i);
          z[i+1] <= z[i] - cordic_kulma(i);
        end else begin
          x[i+1] <= x[i] + (y[i] >>> i);
          y[i+1] <= y[i] - (x[i] >>> i);
          z[i+1] <= z[i] + cordic_kulma(i);
        end
      end
    end

  assign m_valid = v[KIERROKSET];
  assign m_x     = x[KIERROKSET];
  assign m_y     = y[KIERROKSET];
  assign m_z     = z[KIERROKSET];
  // @loppu vaiheet
endmodule
