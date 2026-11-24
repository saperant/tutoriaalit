// Kirjan ajoituskaavion (luku 9) kääre: ajaa luvun 9 testipenkin ja
// tallentaa aaltomuodon. Näytekello `nayte` (jakso 1 ns) antaa
// kaaviolle nanosekunnin tarkkuuden; varsinainen kello on `clk`.
// Tiedoston pääte on .svh, jotta yhteinen testaaja ei aja sitä
// erillisenä esimerkkinä (ks. Makefile).
module jaljitys;
  logic nayte = 1'b0;
  testipenkki t ();
  initial begin
    $dumpfile("rakennus/portitus.vcd");
    $dumpvars(0, jaljitys);
  end
  initial repeat (90) #0.5 nayte = ~nayte;
  initial #45 $finish;
endmodule
