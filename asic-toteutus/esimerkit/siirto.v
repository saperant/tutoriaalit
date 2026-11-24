// Kolmen kiikun siirtorekisteri: kiikkujen välissä ei ole logiikkaa,
// joten pitoaika on tiukimmillaan.
// @alku siirto
module siirto (
  input  wire       clk,
  input  wire       d,
  output reg  [2:0] q
);
  always @(posedge clk) q <= {q[1:0], d};
endmodule
// @loppu siirto
