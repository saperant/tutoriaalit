// Testipenkki: kirjoitetaan 4 tavua ja luetaan ne takaisin. Synkroninen
// luku antaa tuloksen vasta seuraavan kellon reunan jälkeen.
module testipenkki;
  logic       clk = 1'b0;
  logic       kaynnissa = 1'b1;
  logic       kirjoita = 1'b0;
  logic [7:0] kirjoitusosoite = '0, tieto_sisaan = '0, lukuosoite = '0;
  logic [7:0] tieto_ulos;

  muisti dut (.clk, .kirjoita, .kirjoitusosoite, .tieto_sisaan,
              .lukuosoite, .tieto_ulos);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    for (int i = 0; i < 4; i++) begin
      kirjoita = 1'b1;
      kirjoitusosoite = 8'(16 * i);
      tieto_sisaan = 8'hA0 + 8'(i);
      @(posedge clk); #1;
    end
    kirjoita = 1'b0;
    // @alku tarkistus
    for (int i = 0; i < 4; i++) begin
      lukuosoite = 8'(16 * i);
      #1 $display("osoite %3d, ennen reunaa: %h", lukuosoite, tieto_ulos);
      @(posedge clk); #1;
      $display("osoite %3d, reunan jälkeen: %h", lukuosoite, tieto_ulos);
      if (tieto_ulos != 8'hA0 + 8'(i)) $fatal(1, "väärä arvo");
    end
    // @loppu tarkistus
    kaynnissa = 1'b0;
  end
endmodule
