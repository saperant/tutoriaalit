`include "kertoimet.svh"

// @alku biquad
// Toisen asteen IIR-lohko suorassa muodossa I (DF1):
//   y[n] = kavenna(b0 x[n] + b1 x[n-1] + b2 x[n-2] - a1 y[n-1] - a2 y[n-2])
// Näytteet Q1.15, kertoimet Q2.14 järjestyksessä b0, b1, b2, a1, a2.
// Takaisinkytkentä y[n-1] -> y[n] kulkee kertojan, summaimen ja
// saturoinnin läpi yhdessä jaksossa: se on lohkon kriittinen polku,
// eikä sitä voi katkaista rekisterillä muuttamatta suodinta.
module biquad #(
  parameter int DW    = 16,
  parameter int KW    = 16,
  parameter int MURTO = 14,
  parameter logic [5*KW-1:0] K = `SOS0_KERTOIMET
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
  localparam int AW = DW + KW + 3;           // viisi tuloa

  logic eteen;
  assign eteen   = !m_valid || m_ready;
  assign s_ready = eteen;

  logic signed [KW-1:0] b0, b1, b2, a1, a2;
  assign {a2, a1, b2, b1, b0} = K;

  // Tulot omiin täysleveisiin johtoihin (DW + KW bittiä), sitten
  // summa AW bitillä: yksikään välitulos ei katkea.
  localparam int PW = DW + KW;
  logic signed [DW-1:0] x1, x2, y1, y2, y;
  logic signed [PW-1:0] tb0, tb1, tb2, ta1, ta2;
  logic signed [AW-1:0] acc;
  assign tb0 = b0 * s_data;
  assign tb1 = b1 * x1;
  assign tb2 = b2 * x2;
  assign ta1 = a1 * y1;
  assign ta2 = a2 * y2;
  assign acc = AW'(tb0) + AW'(tb1) + AW'(tb2) - AW'(ta1) - AW'(ta2);

  kavenna #(.IW(AW), .OW(DW), .SIIRTO(MURTO)) u_kavenna (acc, y);

  always_ff @(posedge clk)
    if (nollaus) begin
      {x1, x2, y1, y2} <= '0;
      m_valid <= 1'b0;
    end else if (eteen) begin
      if (s_valid) begin
        {x2, x1} <= {x1, s_data};
        {y2, y1} <= {y1, y};
        m_data   <= y;
      end
      m_valid <= s_valid;
    end
endmodule
// @loppu biquad
