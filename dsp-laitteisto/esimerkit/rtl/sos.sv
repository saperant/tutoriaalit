`include "kertoimet.svh"

// @alku sos
// Kahden lohkon kaskadi (neljännen asteen Butterworth). Lohkot ovat
// virtaliitännällä peräkkäin, joten vastapaine kulkee ketjun läpi.
module sos (
  input  logic               clk,
  input  logic               nollaus,
  input  logic               s_valid,
  output logic               s_ready,
  input  logic signed [15:0] s_data,
  output logic               m_valid,
  input  logic               m_ready,
  output logic signed [15:0] m_data
);
  logic               valid1, ready1;
  logic signed [15:0] data1;
  biquad #(.K(`SOS0_KERTOIMET)) u_lohko0 (
    clk, nollaus, s_valid, s_ready, s_data, valid1, ready1, data1);
  biquad #(.K(`SOS1_KERTOIMET)) u_lohko1 (
    clk, nollaus, valid1, ready1, data1, m_valid, m_ready, m_data);
endmodule
// @loppu sos
