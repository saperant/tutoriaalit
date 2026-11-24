// @alku cic
// CIC-desimaattori: N integraattoria sisääntulotaajuudella, desimointi
// R:llä ja N kampaa ulostulotaajuudella. Kertojia ei ole. Kaikki
// laskenta tehdään BW bitillä ja ylivuodot saavat kiertää: kammat
// kumoavat ne, kunhan BW >= BIN + N log2(R) (Hogenauer). Ulostulosta
// pudotetaan BW - BOUT alinta bittiä.
module cic #(
  parameter int N    = 3,
  parameter int R    = 8,
  parameter int BIN  = 12,
  parameter int BW   = 21,
  parameter int BOUT = 16
) (
  input  logic                   clk,
  input  logic                   nollaus,
  input  logic                   s_valid,
  output logic                   s_ready,
  input  logic signed [BIN-1:0]  s_data,
  output logic                   m_valid,
  input  logic                   m_ready,
  output logic signed [BOUT-1:0] m_data
);
  localparam int RW = $clog2(R);

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  logic signed [BW-1:0] integ [N];           // integraattorit
  logic signed [BW-1:0] kampa [N];           // kampojen viive (M = 1)
  logic signed [BW-1:0] ero   [N+1];         // kampaketju
  logic [RW-1:0]        laskuri;
  logic                 desimoi;             // integ[N-1] on näyte R-1

  // Kammat ovat yhdistelmälogiikkaa: ero[i+1] = ero[i] - kampa[i].
  always_comb begin
    ero[0] = integ[N-1];
    for (int i = 0; i < N; i++) ero[i+1] = ero[i] - kampa[i];
  end

  always_ff @(posedge clk)
    if (nollaus) begin
      for (int i = 0; i < N; i++) begin
        integ[i] <= '0;
        kampa[i] <= '0;
      end
      laskuri <= '0;
      desimoi <= 1'b0;
      m_valid <= 1'b0;
    end else if (eteen) begin
      if (s_valid) begin                     // integraattorit
        integ[0] <= integ[0] + BW'(s_data);
        for (int i = 1; i < N; i++) integ[i] <= integ[i] + integ[i-1];
        laskuri <= laskuri + 1'b1;
      end
      desimoi <= s_valid && laskuri == RW'(R - 1);
      if (desimoi) begin                     // kammat
        for (int i = 0; i < N; i++) kampa[i] <= ero[i];
        m_data <= ero[N][BW-1 -: BOUT];
      end
      m_valid <= desimoi;
    end
endmodule
// @loppu cic
