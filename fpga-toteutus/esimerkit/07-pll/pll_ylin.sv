// @alku pll
// 12 MHz:n kide -> PLL -> 48 MHz. Synteesissä (SYNTHESIS on
// määritelty) käytetään iCE40:n PLL-primitiiviä. Simulaatiossa PLL
// korvataan suoralla kytkennällä, koska testi tarkistaa vain logiikan.
module pll_ylin (
  input  logic clk_12,
  output logic led_n
);
  logic clk_48, lukittu;

`ifdef SYNTHESIS
  // Parametrit laskettu komennolla: icepll -i 12 -o 48
  SB_PLL40_PAD #(
    .FEEDBACK_PATH("SIMPLE"),
    .DIVR(4'd0), .DIVF(7'd63), .DIVQ(3'd4), .FILTER_RANGE(3'd1)
  ) pll (
    .PACKAGEPIN(clk_12), .PLLOUTGLOBAL(clk_48), .LOCK(lukittu),
    .RESETB(1'b1), .BYPASS(1'b0)
  );
`else
  assign clk_48  = clk_12;
  assign lukittu = 1'b1;
`endif
// @loppu pll

// @alku nollaus
  // Nollaus vapautuu vasta, kun PLL on lukittunut, ja tahdistetaan
  // 48 MHz:n kelloon kahdella kiikulla.
  logic [1:0] tahdistin = '0;
  logic       nollaus;
  always_ff @(posedge clk_48 or negedge lukittu)
    if (!lukittu) tahdistin <= '0;
    else          tahdistin <= {tahdistin[0], 1'b1};
  assign nollaus = ~tahdistin[1];

  logic [25:0] laskuri;
  always_ff @(posedge clk_48)
    if (nollaus) laskuri <= '0;
    else         laskuri <= laskuri + 1'b1;
  assign led_n = ~laskuri[25];
endmodule
// @loppu nollaus
