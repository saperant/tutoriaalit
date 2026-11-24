// Virheellinen orja protokollatarkistimen testiin.
//
// Orja nostaa RVALIDin ja laskee sen jakson päästä, vaikka isäntä ei
// ole kuitannut vastausta (RREADY = 0). AXI kieltää tämän: VALID saa
// laskea vasta kättelyn jälkeen. Tarkistimen on pysäytettävä simulaatio.
module huono_orja;
  import vaylat::*;

  logic      kello = 1'b0, nollaus_n = 1'b0;
  axil_m2s_t m;
  axil_s2m_t s;
  int        jakso = 0;

  initial forever #5 kello = ~kello;

  axil_tarkistin #(.NIMI("huono")) u_tarkistin (.kello, .nollaus_n,
                                                .m, .s);

  // @alku virhe
  always_comb begin
    m = '0;
    s = '0;
    m.araddr  = 32'h100;
    m.arvalid = (jakso == 2);           // yksi lukupyyntö
    s.arready = 1'b1;
    m.rready  = (jakso >= 6);           // isäntä kuittaa vasta myöhemmin
    s.rvalid  = (jakso == 4);           // VIRHE: vain yhden jakson
    s.rdata   = 32'hDEAD_BEEF;
  end
  // @loppu virhe

  always @(posedge kello) begin
    jakso <= jakso + 1;
    if (jakso == 1) nollaus_n <= 1'b1;
    if (jakso == 10) begin
      $display("virhettä ei havaittu");
      $finish;
    end
  end

endmodule
