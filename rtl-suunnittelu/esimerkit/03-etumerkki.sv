module testipenkki;
  logic signed [7:0] lampotila = -8'sd20;
  logic        [7:0] korjaus   = 8'd5;
  logic signed [7:0] raja      = -8'sd10;

  initial begin
    #1;
    // @alku sudenkuoppa
    // Yksikin etumerkitön operandi tekee koko lausekkeesta
    // etumerkittömän: -20 tulkitaan luvuksi 236.
    $display("lampotila < korjaus: %b", lampotila < korjaus);

    // Oikein: muunnetaan molemmat int-tyyppiin. Etumerkillinen arvo
    // laajennetaan etumerkillä, etumerkitön nollilla.
    $display("int'(lampotila) < int'(korjaus): %b",
             int'(lampotila) < int'(korjaus));
    // @loppu sudenkuoppa

    // @alku siirrot
    $display("raja >>> 1 = %0d (aritmeettinen)", raja >>> 1);
    $display("raja >> 1  = %0d (looginen)", $signed(raja >> 1));
    // @loppu siirrot
  end
endmodule
