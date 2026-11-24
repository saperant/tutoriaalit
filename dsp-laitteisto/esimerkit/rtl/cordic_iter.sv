// @alku kuvaus
// Iteratiivinen CORDIC: yksi kiertovaihe, jota käytetään KIERROKSET
// jaksoa peräkkäin. Siirron määrä vaihtuu kierroksittain, joten
// vaiheessa on muuttuva siirtäjä ja kulmataulukko. Liitäntä ja tulos
// kuten cordic_lh, mutta uusi syöte otetaan vasta edellisen jälkeen.
module cordic_iter #(
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
  // @loppu kuvaus
  `include "cordic_kulmat.svh"
  localparam int CW = $clog2(KIERROKSET);

  logic signed [XW-1:0] xs, ys;
  logic signed [ZW-1:0] zs;
  logic                 kaanna;
  assign xs = {{(XW - 18){s_x[15]}}, s_x, 2'b00};
  assign ys = {{(XW - 18){s_y[15]}}, s_y, 2'b00};
  assign zs = {s_z, 2'b00};
  assign kaanna = s_tila ? s_x[15] : s_z[15] ^ s_z[14];

  // @alku iteraatio
  logic          laskee, tila;
  logic [CW-1:0] i;                          // kierros
  logic signed [XW-1:0] x, y, xi, yi;
  logic signed [ZW-1:0] z, kulma;

  assign s_ready = !laskee && (!m_valid || m_ready);
  assign xi      = x >>> i;                  // muuttuva siirtäjä
  assign yi      = y >>> i;
  assign kulma   = cordic_kulma(32'(i));     // taulukko

  always_ff @(posedge clk)
    if (nollaus) begin
      laskee  <= 1'b0;
      m_valid <= 1'b0;
      i       <= '0;
    end else begin
      if (m_valid && m_ready) m_valid <= 1'b0;
      if (s_valid && s_ready) begin
        tila   <= s_tila;
        x      <= kaanna ? -xs : xs;
        y      <= kaanna ? -ys : ys;
        z      <= kaanna ? zs + ZW'(1 << (ZW - 1)) : zs;
        i      <= '0;
        laskee <= 1'b1;
      end else if (laskee) begin
        if (tila ? y[XW-1] : !z[ZW-1]) begin
          x <= x - yi;
          y <= y + xi;
          z <= z - kulma;
        end else begin
          x <= x + yi;
          y <= y - xi;
          z <= z + kulma;
        end
        i <= i + 1'b1;
        if (i == CW'(KIERROKSET - 1)) begin
          laskee  <= 1'b0;
          m_valid <= 1'b1;
        end
      end
    end

  assign m_x = x;
  assign m_y = y;
  assign m_z = z;
  // @loppu iteraatio
endmodule
