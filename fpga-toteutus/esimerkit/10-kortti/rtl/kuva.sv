// @alku kuva
// Kuvan sisältö: väri lasketaan pikselin paikasta. Kuvassa on valkoinen
// reunus, kahdeksan väripalkkia, pallo ja kaksi heksanumeroa.
module kuva #(
  parameter int PALLO = 32
) (
  input  logic [9:0]  x,
  input  logic [9:0]  y,
  input  logic [9:0]  px,       // pallon vasen yläkulma
  input  logic [9:0]  py,
  input  logic [2:0]  vari,     // pallon väri {sininen, vihreä, punainen}
  input  logic [7:0]  luku,     // näytettävä luku
  output logic [11:0] rgb       // {punainen, vihreä, sininen}, 4 bittiä
);
  // Väripalkin numero 0-7: palkit ovat 80 pikseliä leveitä.
  logic [2:0] palkki;
  always_comb begin
    palkki = '0;
    for (int i = 1; i < 8; i++)
      if (x >= 10'(80 * i)) palkki = 3'(i);
  end

  // Numerot: 8 x 8 pisteen merkit kahdeksankertaisina kohdassa
  // x = 256..383, y = 384..447. Paikka on valittu niin, että merkin
  // rivi ja sarake saadaan suoraan koordinaattien biteistä.
  logic [7:0] rivi;
  fontti merkit (
    .merkki(x[6] ? luku[3:0] : luku[7:4]),
    .rivi(y[5:3]),
    .pikselit(rivi)
  );

  logic reunus, palkeissa, pallossa, numerossa;
  assign reunus    = x == 0 || x == 639 || y == 0 || y == 479;
  assign palkeissa = y >= 16 && y < 112;
  assign pallossa  = x >= px && x < px + 10'(PALLO) &&
                     y >= py && y < py + 10'(PALLO);
  assign numerossa = x >= 256 && x < 384 && y >= 384 && y < 448 &&
                     rivi[3'd7 - x[5:3]];

  always_comb
    if (reunus)         rgb = 12'hfff;
    else if (palkeissa) rgb = {{4{~palkki[1]}}, {4{~palkki[2]}},
                               {4{~palkki[0]}}};
    else if (pallossa)  rgb = {{4{vari[0]}}, {4{vari[1]}}, {4{vari[2]}}};
    else if (numerossa) rgb = 12'hfd0;
    else                rgb = 12'h014;       // tausta: tumma sininen
endmodule
// @loppu kuva
