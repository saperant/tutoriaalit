// 8-bittinen laskuri sallinnalla ja synkronisella nollauksella.
// @alku laskuri
module laskuri (
  input  wire       clk,
  input  wire       nollaa,
  input  wire       sallinta,
  output reg  [7:0] q
);
  always @(posedge clk)
    if (nollaa)        q <= 8'd0;
    else if (sallinta) q <= q + 8'd1;
endmodule
// @loppu laskuri
