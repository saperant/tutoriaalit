// @alku kaare
// Synteesikääre lohkoille, joilla on enemmän nastoja kuin iCE40 UP5K
// -kotelossa (39). Sisääntulot siirretään sisään sarjamuotoisesti
// siirtorekisteriin, ja ulostulon bitit taitetaan XOR:lla kahdeksaan
// nastaan. Jokainen bitti vaikuttaa ulostuloon, joten synteesi ei voi
// poistaa logiikkaa. Kääre lisää saman verran soluja kaikille
// toteutuksille, joten vertailu pysyy reiluna.
module kaare #(
  parameter int TOTEUTUS = 0           // 0 cordic_iter, 1 cordic_lh, 2 nco
) (
  input  logic       clk,
  input  logic       nollaus,
  input  logic       sarja,            // sisääntulojen sarjaväylä
  input  logic       s_valid,
  output logic       s_ready,
  output logic       m_valid,
  input  logic       m_ready,
  output logic [7:0] ulos
);
  logic [48:0] sisaan;                 // tila, x, y, z (1 + 3 * 16)
  always_ff @(posedge clk) sisaan <= {sisaan[47:0], sarja};

  logic [57:0] tulos;                  // x, y (2 * 20) ja z (18)
  if (TOTEUTUS == 0) begin : g_iter
    logic signed [19:0] x, y;
    logic signed [17:0] z;
    cordic_iter u_cordic (clk, nollaus, s_valid, s_ready, sisaan[48],
      sisaan[47:32], sisaan[31:16], sisaan[15:0], m_valid, m_ready, x, y, z);
    assign tulos = {x, y, z};
  end else if (TOTEUTUS == 1) begin : g_lh
    logic signed [19:0] x, y;
    logic signed [17:0] z;
    cordic_lh u_cordic (clk, nollaus, s_valid, s_ready, sisaan[48],
      sisaan[47:32], sisaan[31:16], sisaan[15:0], m_valid, m_ready, x, y, z);
    assign tulos = {x, y, z};
  end else begin : g_nco
    logic signed [11:0] y;
    nco u_nco (clk, nollaus, sisaan[23:0], m_valid, m_ready, y);
    assign s_ready = 1'b1;
    assign tulos   = {46'b0, y};
  end

  always_comb begin
    ulos = '0;
    for (int i = 0; i < 58; i++) ulos[i % 8] = ulos[i % 8] ^ tulos[i];
  end
endmodule
// @loppu kaare
