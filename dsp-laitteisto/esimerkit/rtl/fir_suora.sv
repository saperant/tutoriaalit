`include "kertoimet.svh"

// @alku liitanta
// Suoran muodon FIR-suodin: viivelinja, N kertojaa ja summainpuu.
// Virtaliitäntä valid/ready molemmin puolin. Latenssi kolme jaksoa,
// uusi näyte joka jaksolla.
module fir_suora #(
  parameter int N      = 8,                  // kertoimia
  parameter int DW     = 12,                 // näytteet Q1.11
  parameter int KW     = 16,                 // kertoimet Q1.15
  parameter int SIIRTO = 15,                 // Q2.26 -> Q1.11
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
  localparam int PW = DW + KW;               // tulon leveys
  localparam int AW = PW + $clog2(N);        // summan leveys
  // @loppu liitanta

  // @alku pysaytys
  // Koko liukuhihna pysähtyy, kun ulostulossa on näyte, jota
  // vastaanottaja ei ota. Muuten jokainen vaihe etenee joka jaksolla.
  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;
  // @loppu pysaytys

  // @alku datapolku
  logic signed [DW-1:0] x [N];               // x[n], x[n-1], ...
  logic signed [PW-1:0] p [N];               // tulot
  logic                 v1, v2;              // vaiheiden valid-bitit
  logic signed [AW-1:0] summa;
  logic signed [DW-1:0] y;

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i < N; i++) x[i] <= '0;
      {v1, v2, m_valid} <= '0;
    end else if (eteen) begin
      if (s_valid) begin                     // vaihe 1: viivelinja
        x[0] <= s_data;
        for (int i = 1; i < N; i++) x[i] <= x[i-1];
      end
      for (int i = 0; i < N; i++)            // vaihe 2: tulot
        p[i] <= $signed(K[i*KW +: KW]) * x[i];
      m_data  <= y;                          // vaihe 3: summa
      v1      <= s_valid;
      v2      <= v1;
      m_valid <= v2;
    end

  always_comb begin
    summa = '0;
    for (int i = 0; i < N; i++) summa = summa + AW'(p[i]);
  end

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(SIIRTO)) u_kavenna (summa, y);
  // @loppu datapolku
endmodule
