// Kertoja, jonka tulos ehtii valmistua kahdessa kellojaksossa: vaihe
// vuorottelee, ja tulot ja tulos ladataan samalla, joka toisella
// reunalla. Tulos lasketaan siis edellisestä tuloparista, joka on
// ollut rekistereissä kaksi jaksoa. Ajoitusanalyysille tämä kerrotaan
// monisyklipolkuna.
// @alku kertoja2
module kertoja2 (
  input  wire        clk,
  input  wire        nollaa,
  input  wire [7:0]  a,
  input  wire [7:0]  b,
  output reg  [15:0] tulo
);
  reg       vaihe;
  reg [7:0] a_r, b_r;
  always @(posedge clk) begin
    vaihe <= nollaa ? 1'b0 : ~vaihe;
    if (!vaihe) begin              // joka toinen reuna
      a_r  <= a;
      b_r  <= b;
      tulo <= a_r * b_r;           // edellinen pari: kaksi jaksoa aikaa
    end
  end
endmodule
// @loppu kertoja2
