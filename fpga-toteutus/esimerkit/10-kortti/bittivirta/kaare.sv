// @alku kaare
// Kääre bittivirrasta palautetulle piirille. icebox_vlog kirjoittaa
// bittivirran sisällön Verilog-moduuliksi chip, jonka portit ovat
// rajoitetiedoston nastanimiä. Kääre antaa sille saman liitännän kuin
// kortti_ylin, jotta sama kortin malli ajaa kumpaakin.
module kortti_ylin (
  input  logic       clk_12,
  input  logic       btn1, btn2, btn3,
  input  logic       rx,
  output logic       tx,
  output logic       led1, led2, led3, led4, led5,
  output logic       vga_hs, vga_vs,
  output logic [3:0] vga_r, vga_g, vga_b
);
  chip piiri (
    .clk_12, .btn1, .btn2, .btn3, .rx, .tx,
    .led1, .led2, .led3, .led4, .led5, .vga_hs, .vga_vs,
    .\vga_r[0] (vga_r[0]), .\vga_r[1] (vga_r[1]),
    .\vga_r[2] (vga_r[2]), .\vga_r[3] (vga_r[3]),
    .\vga_g[0] (vga_g[0]), .\vga_g[1] (vga_g[1]),
    .\vga_g[2] (vga_g[2]), .\vga_g[3] (vga_g[3]),
    .\vga_b[0] (vga_b[0]), .\vga_b[1] (vga_b[1]),
    .\vga_b[2] (vga_b[2]), .\vga_b[3] (vga_b[3])
  );
endmodule
// @loppu kaare

// PLL on analoginen lohko, jota bittivirta vain konfiguroi. Mallina on
// sama suora kytkentä kuin RTL-simulaatiossa: kello läpi ja lukitus
// päällä.
module SB_PLL40_PAD #(
  parameter FEEDBACK_PATH = "SIMPLE",
  parameter DELAY_ADJUSTMENT_MODE_FEEDBACK = "FIXED",
  parameter DELAY_ADJUSTMENT_MODE_RELATIVE = "FIXED",
  parameter PLLOUT_SELECT = "GENCLK",
  parameter SHIFTREG_DIV_MODE = 2'b00,
  parameter FDA_FEEDBACK = 4'b0000,
  parameter FDA_RELATIVE = 4'b0000,
  parameter DIVR = 4'b0000,
  parameter DIVF = 7'b0000000,
  parameter DIVQ = 3'b000,
  parameter FILTER_RANGE = 3'b000,
  parameter ENABLE_ICEGATE = 1'b0,
  parameter TEST_MODE = 1'b0
) (
  input  logic       PACKAGEPIN,
  output logic       PLLOUTCORE, PLLOUTGLOBAL, LOCK, SDO,
  input  logic       EXTFEEDBACK, BYPASS, RESETB, LATCHINPUTVALUE,
  input  logic       SDI, SCLK,
  input  logic [7:0] DYNAMICDELAY
);
  assign PLLOUTCORE   = PACKAGEPIN;
  assign PLLOUTGLOBAL = PACKAGEPIN;
  assign LOCK         = 1'b1;
  assign SDO          = 1'b0;
endmodule
