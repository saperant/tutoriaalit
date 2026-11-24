// Testipenkki: syötetään uusi tulo joka jaksolla ja tarkistetaan
// tulokset latenssin päästä. Molemmat versiot ajetaan rinnakkain.
module testipenkki;
  logic        clk = 1'b0;
  logic        kaynnissa = 1'b1;
  logic [7:0]  a = '0, b = '0;
  logic [15:0] tulo1, tulo2;
  logic [15:0] odotetut [$];

  kertoja_lh #(.VAIHEET(1)) yksi (.clk, .a, .b, .tulo(tulo1));
  kertoja_lh #(.VAIHEET(2)) kaksi (.clk, .a, .b, .tulo(tulo2));

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    // @alku tarkistus
    for (int i = 0; i < 40; i++) begin
      a = 8'(37 * i + 11);
      b = 8'(91 * i + 5);
      odotetut.push_back(16'(a) * 16'(b));
      @(posedge clk); #1;
      // Reunan i jälkeen ulostulossa on yksivaiheisen version tulo i-1
      // ja kaksivaiheisen version tulo i-2.
      if (i >= 1 && tulo1 != odotetut[i - 1]) $fatal(1, "1 vaihe");
      if (i >= 2 && tulo2 != odotetut[i - 2]) $fatal(1, "2 vaihetta");
    end
    // @loppu tarkistus
    $display("latenssi 2 ja 3 kellojaksoa, 40 tuloa oikein");
    kaynnissa = 1'b0;
  end
endmodule
