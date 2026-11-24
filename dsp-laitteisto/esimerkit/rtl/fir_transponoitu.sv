`include "kertoimet.svh"

// Transponoidun muodon FIR: jokainen näyte kerrotaan kaikilla
// kertoimilla samassa jaksossa, ja osasummat kulkevat rekisteriketjussa.
// Latenssi yksi jakso. Liitäntä kuten fir_suora.
module fir_transponoitu #(
  parameter int N      = 8,
  parameter int DW     = 12,
  parameter int KW     = 16,
  parameter int SIIRTO = 15,
  parameter logic [N*KW-1:0] K = `FIR_KERTOIMET
) (
  input  logic                 clk,
  input  logic                 nollaus,
  input  logic                 s_valid,
  output logic                 s_ready,
  input  logic signed [DW-1:0] s_data,
  output logic                 m_valid,
  input  logic                 m_ready,
  output logic signed [DW-1:0] m_data
);
  localparam int PW = DW + KW;
  localparam int AW = PW + $clog2(N);

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  // @alku datapolku
  // z[i] on osasumma h[i] x[n-1] + h[i+1] x[n-2] + ... edelliseltä
  // jaksolta. Uusi näyte x kerrotaan kaikilla kertoimilla kerralla.
  logic signed [AW-1:0] z [1:N-1];
  logic signed [PW-1:0] p [N];
  logic signed [AW-1:0] summa;
  logic signed [DW-1:0] y;

  always_comb
    for (int i = 0; i < N; i++) p[i] = $signed(K[i*KW +: KW]) * s_data;
  assign summa = AW'(p[0]) + z[1];

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 1; i < N; i++) z[i] <= '0;
      m_valid <= 1'b0;
    end else if (eteen) begin
      if (s_valid) begin
        for (int i = 1; i < N - 1; i++) z[i] <= AW'(p[i]) + z[i+1];
        z[N-1] <= AW'(p[N-1]);
        m_data <= y;
      end
      m_valid <= s_valid;
    end

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(SIIRTO)) u_kavenna (summa, y);
  // @loppu datapolku
endmodule
