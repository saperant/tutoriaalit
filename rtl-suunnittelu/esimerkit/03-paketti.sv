// @alku paketti
// Paketti kokoaa tyypit, vakiot ja funktiot, joita usea moduuli käyttää.
package vayla_pkg;
  localparam int OSOITELEVEYS = 4;
  typedef logic [OSOITELEVEYS-1:0] osoite_t;

  typedef enum logic [1:0] {LUKU, KIRJOITUS, TYHJA} laji_t;

  typedef struct packed {
    laji_t      laji;
    osoite_t    osoite;
    logic [7:0] data;
    logic       pariteetti;          // pariton pariteetti muista kentistä
  } sanoma_t;

  // Funktio on kombinaatiologiikkaa: ei viiveitä, ei muistia. Sana
  // automatic antaa jokaiselle kutsulle omat paikalliset muuttujat.
  function automatic osoite_t bin_gray(osoite_t b);
    return b ^ (b >> 1);
  endfunction

  function automatic osoite_t gray_bin(osoite_t g);
    osoite_t b;
    b = g;
    for (int i = 1; i < OSOITELEVEYS; i++) b ^= g >> i;
    return b;
  endfunction

  function automatic logic pariton(laji_t l, osoite_t o, logic [7:0] d);
    return ~^{l, o, d};
  endfunction
endpackage
// @loppu paketti

// @alku lahettaja
// Nimetty tuonti: vain luetellut nimet tulevat näkyviin.
module lahettaja
  import vayla_pkg::sanoma_t, vayla_pkg::laji_t, vayla_pkg::osoite_t,
         vayla_pkg::pariton;
(
  input  laji_t      laji,
  input  osoite_t    osoite,
  input  logic [7:0] data,
  output sanoma_t    sanoma
);
  always_comb begin
    sanoma.laji       = laji;
    sanoma.osoite     = osoite;
    sanoma.data       = data;
    sanoma.pariteetti = pariton(laji, osoite, data);
  end
endmodule
// @loppu lahettaja

// @alku tarkistin
// Nimiavaruusviittaus ilman tuontia: paketti::nimi.
module tarkistin (
  input  vayla_pkg::sanoma_t sanoma,
  output logic               ehja
);
  assign ehja = sanoma.pariteetti ==
      vayla_pkg::pariton(sanoma.laji, sanoma.osoite, sanoma.data);
endmodule
// @loppu tarkistin

module testipenkki;
  import vayla_pkg::*;               // testipenkissä jokeri on kätevä

  laji_t      laji;
  osoite_t    osoite;
  logic [7:0] data;
  sanoma_t    sanoma, linjalla;
  logic       ehja;
  int         eroja = 0;

  lahettaja u_l (.laji, .osoite, .data, .sanoma);
  tarkistin u_t (.sanoma(linjalla), .ehja);

  initial begin
    // Gray-koodi: peräkkäiset arvot eroavat yhdellä bitillä, ja
    // muunnos takaisin palauttaa alkuperäisen.
    for (int i = 0; i < 16; i++) begin
      osoite_t g, seuraava;
      g        = bin_gray(osoite_t'(i));
      seuraava = bin_gray(osoite_t'(i + 1));
      if ($countones(g ^ seuraava) != 1 || gray_bin(g) != osoite_t'(i))
        eroja++;
    end
    $display("gray: 5 -> %b -> %0d, virheitä %0d",
             bin_gray(4'd5), gray_bin(bin_gray(4'd5)), eroja);

    laji = KIRJOITUS; osoite = 4'hA; data = 8'h3C;
    #1 linjalla = sanoma;
    #1 $display("sanoma %b_%b_%b_%b (%0d bittiä), ehjä %b",
                sanoma.laji, sanoma.osoite, sanoma.data,
                sanoma.pariteetti, $bits(sanoma), ehja);
    linjalla.data[2] = ~linjalla.data[2];      // yhden bitin virhe
    #1 $display("bitti käännetty: ehjä %b", ehja);
    if (eroja != 0 || ehja) $fatal(1, "paketin funktiot toimivat väärin");
  end
endmodule
