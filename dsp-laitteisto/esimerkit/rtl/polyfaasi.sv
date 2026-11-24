`include "kertoimet.svh"

// @alku kuvaus
// Polyfaasidesimaattori: N-kertoiminen alipäästö ja desimointi M:llä.
// Suora toteutus laskisi jokaisen ulostulon ja heittäisi M - 1
// pois, eli N kertojaa. Tässä jokainen sisääntulo laskee vain sen
// haaran (N/M kerrointa), johon se kuuluu, ja haarojen summat
// kertyvät. Kertojia on N/M ja ulostulo valmistuu joka M:nnellä
// näytteellä. Tulos on bitilleen sama kuin suoran rakenteen.
module polyfaasi #(
  parameter int N      = 16,
  parameter int M      = 4,                  // desimointi, N:n tekijä
  parameter int DW     = 12,
  parameter int KW     = 16,
  parameter int SIIRTO = 15,
  parameter logic [N*KW-1:0] K = `POLYFAASI_KERTOIMET
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
  // @loppu kuvaus
  localparam int L  = N / M;                 // kertoimia haarassa
  localparam int PW = DW + KW;
  localparam int AW = PW + $clog2(N);
  localparam int VW = $clog2(M);

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  // @alku datapolku
  // Haara p = (-n) mod M: ensimmäinen näyte (n = 0) päättää ulostulon
  // y[0], seuraavat haarat M-1, ..., 1 aloittavat seuraavan summan.
  logic signed [DW-1:0] x [N];
  logic [VW-1:0]        vaihe, vaihe1, vaihe2;
  logic                 v1, v2;
  logic signed [PW-1:0] q [L];
  logic signed [AW-1:0] osa, acc, uusi;
  logic signed [DW-1:0] y;

  always_comb begin
    osa = '0;
    for (int j = 0; j < L; j++) osa = osa + AW'(q[j]);
    uusi = (vaihe2 == VW'(M - 1) ? '0 : acc) + osa;
  end

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i < N; i++) x[i] <= '0;
      {v1, v2, m_valid} <= '0;
      vaihe <= '0;
      acc   <= '0;
    end else if (eteen) begin
      if (s_valid) begin                     // vaihe 1: viivelinja
        x[0] <= s_data;
        for (int i = 1; i < N; i++) x[i] <= x[i-1];
        vaihe <= vaihe - 1'b1;
      end
      vaihe1 <= vaihe;
      v1     <= s_valid;
      for (int j = 0; j < L; j++)            // vaihe 2: haaran tulot
        q[j] <= $signed(K[(M*j + 32'(vaihe1))*KW +: KW]) * x[M*j];
      vaihe2 <= vaihe1;
      v2     <= v1;
      if (v2) acc <= uusi;                   // vaihe 3: kertymä
      m_valid <= v2 && vaihe2 == '0;
      if (v2 && vaihe2 == '0) m_data <= y;
    end

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(SIIRTO)) u_kavenna (uusi, y);
  // @loppu datapolku
endmodule
