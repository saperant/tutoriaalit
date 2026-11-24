// Tehoalue: kytkettävä alue, sen ohjain, kellon portitus ja eristys.
//
// Ohjain sammuttaa ja käynnistää alueen oikeassa järjestyksessä:
//   sammutus:   eristä lähdöt → pysäytä kello → katkaise virta
//   käynnistys: kytke virta → odota → nollaus kellon käydessä →
//               vapauta nollaus → poista eristys
// Simulaatiossa virran katkaisu tuhoaa alueen tilan (arvo 0xA5), kuten
// oikeassa piirissä, jossa tila katoaa ilman säilytysrekistereitä.
/* verilator lint_off DECLFILENAME */

// @alku icg
// Kellon portitussolu (ICG): salpa pitää sallinnan vakaana kellon
// ollessa ylhäällä, joten portitettuun kelloon ei synny lyhyitä pulsseja.
module icg (
  input  logic kello,
  input  logic salli,
  output logic portitettu
);
  logic salpa;
  always_latch
    if (!kello) salpa = salli;
  assign portitettu = kello & salpa;
endmodule
// @loppu icg

module tehoalue_ohjain (
  input  logic       kello,
  input  logic       nollaus_n,
  input  logic       sammuta,
  input  logic       kaynnista,
  output logic       eristys,
  output logic       kello_paalla,
  output logic       virta,
  output logic       alue_nollaus_n,
  output logic [2:0] vaihe
);
  // @alku ohjain
  typedef enum logic [2:0] {PAALLA, ERISTA, KELLO_POIS, POIS,
                            VIRTA_PAALLE, NOLLAUS, VAPAUTA} tila_t;
  tila_t      tila;
  logic [1:0] odotus;

  assign vaihe          = tila;
  assign eristys        = (tila != PAALLA);
  assign kello_paalla   = (tila == PAALLA || tila == ERISTA ||
                           tila == NOLLAUS || tila == VAPAUTA);
  assign virta          = (tila != POIS);
  assign alue_nollaus_n = (tila != NOLLAUS && tila != VIRTA_PAALLE);

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila   <= PAALLA;
      odotus <= '0;
    end else begin
      case (tila)
        PAALLA:       if (sammuta) tila <= ERISTA;
        ERISTA:       tila <= KELLO_POIS;
        KELLO_POIS:   tila <= POIS;
        POIS:         if (kaynnista) begin
                        tila   <= VIRTA_PAALLE;
                        odotus <= 2'd3;     // jännitteen asettuminen
                      end
        VIRTA_PAALLE: if (odotus == 0) tila <= NOLLAUS;
                      else odotus <= odotus - 2'd1;
        NOLLAUS:      tila <= VAPAUTA;
        VAPAUTA:      tila <= PAALLA;
        default:      tila <= PAALLA;
      endcase
    end
  end
  // @loppu ohjain
endmodule

// Kytkettävän alueen logiikka: laskuri omalla, portitetulla kellolla.
module alue_laskuri (
  input  logic       kello,
  input  logic       nollaus_n,
  input  logic       virta,
  output logic [7:0] arvo
);
  always_ff @(posedge kello or negedge nollaus_n or negedge virta)
    if (!virta)          arvo <= 8'hA5;     // tila tuhoutuu
    else if (!nollaus_n) arvo <= 8'h00;
    else                 arvo <= arvo + 8'd1;
endmodule

module tehoalue (
  input  logic       kello,
  input  logic       nollaus_n,
  input  logic       sammuta,
  input  logic       kaynnista,
  output logic [7:0] lahto,          // aina päällä olevalle alueelle
  output logic [7:0] sisainen,       // alueen oma arvo (vain seurantaan)
  output logic [2:0] vaihe
);
  logic eristys, kello_paalla, alue_nollaus_n, alue_kello;
  /* verilator lint_off SYNCASYNCNET */
  logic virta;              // testipenkki lukee tämän kellotetusti
  /* verilator lint_on SYNCASYNCNET */

  tehoalue_ohjain u_ohjain (.kello, .nollaus_n, .sammuta, .kaynnista,
                            .eristys, .kello_paalla, .virta,
                            .alue_nollaus_n, .vaihe);
  icg u_icg (.kello, .salli(kello_paalla), .portitettu(alue_kello));
  alue_laskuri u_alue (.kello(alue_kello), .nollaus_n(alue_nollaus_n),
                       .virta, .arvo(sisainen));

  // @alku eristys
  // Eristyssolu: sammutetun alueen lähtö pakotetaan tunnettuun arvoon,
  // jotta aina päällä oleva logiikka ei näe kelluvaa signaalia.
  assign lahto = eristys ? 8'h00 : sisainen;
  // @loppu eristys
endmodule
