module rekisteri8 (
  input  logic       clk,
  input  logic [7:0] d,
  output logic [7:0] q
);
  always_ff @(posedge clk) q <= d;
endmodule

module testipenkki;
  logic        clk = 1'b0;
  logic [7:0]  d = 8'hA5;
  logic [15:0] q16;                  // @virhe
  logic [7:0]  q;
  // Portti q on 8-bittinen, mutta siihen kytketään 16-bittinen signaali.
  rekisteri8 u_r (.clk, .d, .q(q16)); // @virhe
  rekisteri8 u_k (.clk, .d, .q);
  initial begin
    #1 clk = 1'b1;
    #1 $display("q = %h", q);
  end
endmodule
