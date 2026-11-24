`include "kertoimet.svh"

// Symmetrinen FIR: lineaarivaiheisen suotimen kertoimet toistuvat
// peilikuvana (h[k] = h[N-1-k]), joten näytepari lasketaan ensin yhteen
// ja kerrotaan kerran. Kertojia on N/2. Latenssi kolme jaksoa.
module fir_symmetrinen #(
  parameter int N      = 8,                  // parillinen
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
  localparam int H  = N / 2;
  localparam int PW = DW + 1 + KW;           // esisumma on bitin leveämpi
  localparam int AW = PW + $clog2(H);

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  // @alku datapolku
  logic signed [DW-1:0] x [N];
  logic signed [DW:0]   e [H];               // esisummat
  logic signed [PW-1:0] p [H];
  logic                 v1, v2;
  logic signed [AW-1:0] summa;
  logic signed [DW-1:0] y;

  always_comb
    for (int i = 0; i < H; i++) e[i] = x[i] + x[N-1-i];

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i < N; i++) x[i] <= '0;
      {v1, v2, m_valid} <= '0;
    end else if (eteen) begin
      if (s_valid) begin
        x[0] <= s_data;
        for (int i = 1; i < N; i++) x[i] <= x[i-1];
      end
      for (int i = 0; i < H; i++)
        p[i] <= $signed(K[i*KW +: KW]) * e[i];
      m_data  <= y;
      v1      <= s_valid;
      v2      <= v1;
      m_valid <= v2;
    end
  // @loppu datapolku

  always_comb begin
    summa = '0;
    for (int i = 0; i < H; i++) summa = summa + AW'(p[i]);
  end

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(SIIRTO)) u_kavenna (summa, y);
endmodule
