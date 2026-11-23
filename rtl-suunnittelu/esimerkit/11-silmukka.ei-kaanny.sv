// Kättely kelvollinen/valmis (valid/ready) yhden moduulin sisällä.
// Sääntö: lähettäjän kelvollinen ei saa riippua vastaanottajan
// valmis-signaalista. Jos riippuu, ja vastaanottajan valmis riippuu
// kelvollisesta, syntyy kombinatorinen silmukka.
module tuottaja_kuluttaja (
  input  logic clk,
  input  logic rst_n,
  input  logic data_saatavilla,
  input  logic kiireinen,
  output logic siirto
);
  logic kelvollinen, valmis;

  // @alku kattely
  assign kelvollinen = data_saatavilla
                       && valmis        // @virhe: riippuu valmiista
                       ;
  assign valmis      = kelvollinen && !kiireinen;
  // @loppu kattely

  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) siirto <= 1'b0;
    else        siirto <= kelvollinen && valmis;
endmodule

module testipenkki;
  logic clk = 1'b0, rst_n = 1'b0, data_saatavilla = 1'b1;
  logic kiireinen = 1'b0, siirto;
  tuottaja_kuluttaja u (.clk, .rst_n, .data_saatavilla, .kiireinen,
                        .siirto);
  initial begin
    #1 rst_n = 1'b1;
    #1 clk = 1'b1;
    #1 $display("siirto = %b", siirto);
  end
endmodule
