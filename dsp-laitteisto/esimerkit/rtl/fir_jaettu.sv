`include "kertoimet.svh"

// @alku liitanta
// Aikamultipleksoitu FIR: yksi kertoja-kertymä (MAC) laskee N kerrointa
// peräkkäisinä jaksoina. Näyte otetaan vastaan vain levossa, joten
// näytteiden väli on vähintään N + 1 kellojaksoa. Liitäntä kuten
// fir_suora; ready-signaali kertoo vastapaineesta.
module fir_jaettu #(
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
  // @loppu liitanta
  localparam int PW = DW + KW;
  localparam int AW = PW + $clog2(N);
  localparam int CW = $clog2(N);

  // @alku ohjaus
  logic signed [DW-1:0] x [N];
  logic                 laskee;
  logic [CW-1:0]        vaihe;               // käsiteltävä kerroin
  logic signed [AW-1:0] acc, seuraava;
  logic signed [PW-1:0] tulo;
  logic signed [DW-1:0] y;

  // Uusi näyte, kun lepotilassa ja edellinen tulos on luettu.
  assign s_ready = !laskee && (!m_valid || m_ready);

  // Yksi kertoja: multiplekserit valitsevat vaiheen kertoimen ja näytteen.
  assign tulo     = $signed(K[vaihe*KW +: KW]) * x[vaihe];
  assign seuraava = acc + AW'(tulo);

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i < N; i++) x[i] <= '0;
      laskee  <= 1'b0;
      vaihe   <= '0;
      acc     <= '0;
      m_valid <= 1'b0;
    end else begin
      if (m_valid && m_ready) m_valid <= 1'b0;
      if (s_valid && s_ready) begin          // lepo -> laskenta
        x[0] <= s_data;
        for (int i = 1; i < N; i++) x[i] <= x[i-1];
        acc    <= '0;
        vaihe  <= '0;
        laskee <= 1'b1;
      end else if (laskee) begin             // yksi MAC jaksossa
        acc   <= seuraava;
        vaihe <= vaihe + 1'b1;
        if (vaihe == CW'(N - 1)) begin
          m_data  <= y;
          m_valid <= 1'b1;
          laskee  <= 1'b0;
        end
      end
    end

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(SIIRTO)) u_kavenna (seuraava, y);
  // @loppu ohjaus
endmodule
