// Virheellinen: kun valinta = 0, y säilyttää arvonsa -> salpa.
module valitsin_salpa (                   // @virhe
  input  logic       valinta,             // @virhe
  input  logic [7:0] a,                   // @virhe
  output logic [7:0] y                    // @virhe
);                                        // @virhe
  always_comb if (valinta) y = a;         // @virhe
endmodule                                 // @virhe

// Oikein: oletusarvo ensin, joten jokainen polku asettaa y:n.
module valitsin (
  input  logic       valinta,
  input  logic [7:0] a,
  output logic [7:0] y
);
  always_comb begin
    y = '0;
    if (valinta) y = a;
  end
endmodule

module testipenkki;
  logic [7:0] a = 8'h3C, y;
  logic [7:0] y_salpa;                    // @virhe
  logic       valinta = 1'b1;
  valitsin       u_oikea (.valinta, .a, .y);
  valitsin_salpa u_salpa (.valinta, .a, .y(y_salpa)); // @virhe
  initial begin
    #1 valinta = 1'b0;
    #1 $display("valinta = 0: y = %h", y);
    $display("salvan arvo %h", y_salpa);  // @virhe
  end
endmodule
