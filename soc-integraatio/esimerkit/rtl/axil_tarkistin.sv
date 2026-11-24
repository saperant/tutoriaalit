// AXI4-Lite-protokollan tarkistin (vain simulaatioon).
//
// Tarkistin kytketään yhteen isäntä–orja-liitäntään ja valvoo
// AMBA-määrittelyn kättelysääntöjä:
//   1. Kun VALID on noussut, se pysyy ylhäällä ja sisältö pysyy samana,
//      kunnes READY kuittaa siirron.
//   2. Vastausta (R tai B) ei tule ilman avointa pyyntöä.
// Säännöt kirjoitetaan välittöminä väittäminä edellisen jakson tilaa
// vasten, joten ne toimivat kaikissa simulaattoreissa.
module axil_tarkistin
  import vaylat::*;
#(
  parameter string NIMI = "axil"
)(
  input logic      kello,
  input logic      nollaus_n,
  input axil_m2s_t m,
  input axil_s2m_t s
);

  axil_m2s_t   m_ed;
  axil_s2m_t   s_ed;
  int unsigned luvut, kirjoitukset;   // avoimet pyynnöt

  // @alku saanto
  /* verilator lint_off SYNCASYNCNET */
  always_ff @(posedge kello) begin
    if (nollaus_n) begin
      if (m_ed.arvalid && !s_ed.arready)
        assert (m.arvalid && m.araddr == m_ed.araddr)
          else $error("%s: AR muuttui ennen kättelyä", NIMI);
      if (m_ed.awvalid && !s_ed.awready)
        assert (m.awvalid && m.awaddr == m_ed.awaddr)
          else $error("%s: AW muuttui ennen kättelyä", NIMI);
      if (m_ed.wvalid && !s_ed.wready)
        assert (m.wvalid && m.wdata == m_ed.wdata &&
                m.wstrb == m_ed.wstrb)
          else $error("%s: W muuttui ennen kättelyä", NIMI);
      if (s_ed.rvalid && !m_ed.rready)
        assert (s.rvalid && s.rdata == s_ed.rdata &&
                s.rresp == s_ed.rresp)
          else $error("%s: R muuttui ennen kättelyä", NIMI);
      if (s_ed.bvalid && !m_ed.bready)
        assert (s.bvalid && s.bresp == s_ed.bresp)
          else $error("%s: B muuttui ennen kättelyä", NIMI);
      assert (!s.rvalid || luvut != 0)
        else $error("%s: R-vastaus ilman lukupyyntöä", NIMI);
      assert (!s.bvalid || kirjoitukset != 0)
        else $error("%s: B-vastaus ilman kirjoituspyyntöä", NIMI);
    end
  end
  /* verilator lint_on SYNCASYNCNET */
  // @loppu saanto

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      m_ed         <= '0;
      s_ed         <= '0;
      luvut        <= 0;
      kirjoitukset <= 0;
    end else begin
      m_ed <= m;
      s_ed <= s;
      luvut <= luvut + ((m.arvalid && s.arready) ? 1 : 0)
                     - ((s.rvalid && m.rready) ? 1 : 0);
      kirjoitukset <= kirjoitukset + ((m.awvalid && s.awready) ? 1 : 0)
                                   - ((s.bvalid && m.bready) ? 1 : 0);
    end
  end

endmodule
