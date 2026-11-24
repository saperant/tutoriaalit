// Testipenkki: tehoalueen sammutus- ja käynnistyssekvenssi.
//
// Jokaisesta vaiheen vaihdosta tulostetaan ohjaussignaalit, alueen oma
// arvo ja eristetty lähtö.
module tb_tehoalue;
  logic       kello = 1'b0, nollaus_n = 1'b0;
  logic       sammuta = 1'b0, kaynnista = 1'b0;
  logic [7:0] lahto, sisainen;
  logic [2:0] vaihe, edellinen = 3'd7;
  int         jakso = 0;

  localparam string NIMET [7] = '{"PAALLA", "ERISTA", "KELLO_POIS",
    "POIS", "VIRTA_PAALLE", "NOLLAUS", "VAPAUTA"};

  tehoalue u_alue (.kello, .nollaus_n, .sammuta, .kaynnista, .lahto,
                   .sisainen, .vaihe);

  initial forever #5 kello = ~kello;

`ifdef JALJITYS
  // Aaltomuoto kirjan ajoituskaaviota varten (Makefilen kaaviokohde).
  initial begin
    $dumpfile("build/tehoalue.vcd");
    $dumpvars(0, tb_tehoalue);
  end
`endif
  initial #15 nollaus_n = 1'b1;

  always @(posedge kello) begin
    jakso <= jakso + 1;
    sammuta   <= (jakso == 8);
    kaynnista <= (jakso == 14);
    if (jakso >= 2 && vaihe != edellinen) begin
      $display("jakso %2d  %-12s eristys=%b kello=%b virta=%b",
               jakso, NIMET[vaihe], u_alue.eristys,
               u_alue.kello_paalla, u_alue.virta);
      $display("          alue: 0x%h%h  eristetty lähtö: 0x%h%h",
               sisainen[7:4], sisainen[3:0], lahto[7:4], lahto[3:0]);
      edellinen <= vaihe;
    end
    if (jakso == 26) begin
      $display("lopuksi   alue: 0x%h  lähtö: 0x%h", sisainen, lahto);
      $finish;
    end
  end
endmodule
