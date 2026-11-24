// Kellon portitus: pelkkä JA-portti vs. salpaan perustuva
// portituslohko (integrated clock gate, ICG). Sallinta muuttuu
// kellon ollessa ylhäällä, kuten se logiikan viiveen vuoksi tekee.

// @alku icg
// Salpa päästää sallinnan läpi vain, kun kello on alhaalla, joten
// portitettu kello ei voi katketa eikä alkaa kesken korkean vaiheen.
module icg (input logic clk, sallinta, output logic gclk);
  logic salvattu;
  always_latch if (!clk) salvattu = sallinta;
  assign gclk = clk & salvattu;
endmodule
// @loppu icg

// @alku testipenkki
module testipenkki;
  logic clk = 1'b0, kaynnissa = 1'b1, sallinta = 1'b0;
  logic gclk_and, gclk_icg;
  realtime nousu_and, nousu_icg;

  assign gclk_and = clk & sallinta;          // virheellinen tapa
  icg u_icg (.clk, .sallinta, .gclk(gclk_icg));

  initial while (kaynnissa) #5 clk = ~clk;   // jakso 10 ns

  // Tulostetaan kunkin portitetun kellon korkeiden pulssien kestot.
  always @(posedge gclk_and) nousu_and <= $realtime;
  always @(negedge gclk_and)
    $display("%5.1f ns  JA-portti: pulssi %3.1f ns", $realtime,
             $realtime - nousu_and);
  always @(posedge gclk_icg) nousu_icg <= $realtime;
  always @(negedge gclk_icg)
    $display("%5.1f ns  ICG:       pulssi %3.1f ns", $realtime,
             $realtime - nousu_icg);

  initial begin
    #7  sallinta = 1'b1;       // kello on ylhäällä (5–10 ns)
    #20 sallinta = 1'b0;       // 27 ns: kello ylhäällä (25–30 ns)
    #20 kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
