// Virheellinen: estävä sijoitus kellotetussa lohkossa. vaihe2 saa
// d:n arvon jo samalla reunalla, ja kahden vaiheen viive katoaa.
module viive_estava (                     // @virhe
  input  logic       clk,                 // @virhe
  input  logic [7:0] d,                   // @virhe
  output logic [7:0] vaihe2               // @virhe
);                                        // @virhe
  logic [7:0] vaihe1;                     // @virhe
  always_ff @(posedge clk) begin          // @virhe
    vaihe1 = d;                           // @virhe
    vaihe2 = vaihe1;                      // @virhe
  end                                     // @virhe
endmodule                                 // @virhe

// Oikein: ei-estävät sijoitukset luetaan reunalla ennen päivitystä.
module viive (
  input  logic       clk,
  input  logic [7:0] d,
  output logic [7:0] vaihe2
);
  logic [7:0] vaihe1;
  always_ff @(posedge clk) begin
    vaihe1 <= d;
    vaihe2 <= vaihe1;
  end
endmodule

module testipenkki;
  logic       clk = 1'b0;
  logic [7:0] d = 8'h11, q;
  logic [7:0] q_estava;                                 // @virhe
  viive        u_oikea  (.clk, .d, .vaihe2(q));
  viive_estava u_estava (.clk, .d, .vaihe2(q_estava));  // @virhe
  initial begin
    #1 clk = 1'b1;
    #1 begin clk = 1'b0; d = 8'h22; end
    #1 clk = 1'b1;
    #1 $display("kahden reunan jälkeen q = %h", q);
    $display("estävä versio %h", q_estava);             // @virhe
  end
endmodule
