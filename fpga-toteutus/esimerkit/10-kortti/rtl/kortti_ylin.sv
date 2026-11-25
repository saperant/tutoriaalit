// @alku ylin
// Ylin taso iCEBreaker-kortille: PLL, nollaus ja nastat. Kortin
// 12 MHz:n kiteestä tehdään PLL:llä 25,125 MHz:n pikselikello
// (icepll -i 12 -o 25.175). Simulaatiossa PLL on suora kytkentä, ja
// kortin malli syöttää kellon pikselikellon taajuudella.
module kortti_ylin (
  input  logic       clk_12,
  input  logic       btn1, btn2, btn3,      // 1 = painettu
  input  logic       rx,
  output logic       tx,
  output logic       led1, led2, led3, led4, led5,
  output logic       vga_hs, vga_vs,
  output logic [3:0] vga_r, vga_g, vga_b
);
  logic clk, lukittu;

`ifdef SYNTHESIS
  SB_PLL40_PAD #(
    .FEEDBACK_PATH("SIMPLE"),
    .DIVR(4'd0), .DIVF(7'd66), .DIVQ(3'd5), .FILTER_RANGE(3'd1)
  ) pll (
    .PACKAGEPIN(clk_12), .PLLOUTGLOBAL(clk), .LOCK(lukittu),
    .RESETB(1'b1), .BYPASS(1'b0)
  );
`else
  assign clk     = clk_12;
  assign lukittu = 1'b1;
`endif

  // Nollaus vapautuu, kun PLL on lukittunut (luku 7).
  logic [1:0] tahdistin = '0;
  always_ff @(posedge clk or negedge lukittu)
    if (!lukittu) tahdistin <= '0;
    else          tahdistin <= {tahdistin[0], 1'b1};

  demo ydin (
    .clk, .nollaus(~tahdistin[1]),
    .painike({btn3, btn2, btn1}), .rx, .tx,
    .led({led5, led4, led3, led2, led1}),
    .hsync_n(vga_hs), .vsync_n(vga_vs),
    .rgb({vga_r, vga_g, vga_b})
  );
endmodule
// @loppu ylin
