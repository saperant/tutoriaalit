// Verilogin implisiittinen johto: tuntematon nimi porttikytkennässä
// luo hiljaa 1-bittisen johdon. Kirjoitusvirhe "tulso" ei ole
// käännösvirhe, ellei rivi `default_nettype none ole käytössä.
// Lint-työkalut varoittavat (Verilatorissa IMPLICIT, WIDTHEXPAND).
`default_nettype none
`default_nettype wire                       // @virhe

module rekisteri8 (
  input  wire       clk,
  input  wire [7:0] d,
  output reg  [7:0] q
);
  always @(posedge clk) q <= d;
endmodule

module testipenkki;
  reg        clk = 1'b0;
  reg  [7:0] d = 8'h5A;
  wire [7:0] tulos;
  rekisteri8 u_r (.clk(clk), .d(d), .q(tulso));   // @virhe
  rekisteri8 u_k (.clk(clk), .d(d), .q(tulos));
  initial begin
    #1 clk = 1'b1;
    #1 $display("tulos = %h", tulos);
  end
endmodule

`default_nettype wire                       // palautetaan oletus
