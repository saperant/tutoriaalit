// Asynkronisesti nollautuva laskuri ja nollauksen tahdistin: nollaus
// alkaa heti, mutta vapautuu kellon tahdissa kaikille kiikuille.
// @alku nollaus
module nollaus (
  input  wire        clk,
  input  wire        nollaa_n,        // ulkoinen, asynkroninen
  output reg  [15:0] q
);
  reg t1, t2;                         // tahdistin
  always @(posedge clk or negedge nollaa_n)
    if (!nollaa_n) {t2, t1} <= 2'b00;
    else           {t2, t1} <= {t1, 1'b1};
  always @(posedge clk or negedge t2) // t2 nollaa laskurin
    if (!t2) q <= 16'd0;
    else     q <= q + 16'd1;
endmodule
// @loppu nollaus
