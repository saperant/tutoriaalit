// @alku dekooderi
// Käskydekooderi: käskyn laji tunnistetaan ylimmistä biteistä, ja
// loput bitit ovat operandeja. Kysymysmerkki on "ei väliä" -bitti.
typedef enum logic [2:0] {LATAA, TALLETA, LASKE, HYPPY, PYSAYTA, LAITON}
    laji_t;

module dekooderi (
  input  logic [7:0] kasky,
  output laji_t      laji
);
  always_comb begin
    unique case (kasky) inside
      8'b00??_????: laji = LATAA;      // 00 + rekisteri + osoite
      8'b01??_????: laji = TALLETA;
      8'b10??_????: laji = LASKE;      // 10 + operaatio + rekisterit
      8'b110?_????: laji = HYPPY;      // 110 + siirtymä
      8'b1111_1111: laji = PYSAYTA;
      default:      laji = LAITON;
    endcase
  end
endmodule
// @loppu dekooderi

// @alku keskeytys
// Prioriteetti casez-lauseella: ensimmäinen osuva haara voittaa, joten
// haarojen järjestys on osa logiikkaa. Alin pyyntö on tärkein.
module keskeytysvalitsin (
  input  logic [3:0] pyynnot,
  output logic [1:0] numero,
  output logic       odottaa
);
  always_comb begin
    odottaa = 1'b1;
    casez (pyynnot)
      4'b???1: numero = 2'd0;
      4'b??10: numero = 2'd1;
      4'b?100: numero = 2'd2;
      4'b1000: numero = 2'd3;
      default: begin numero = 2'd0; odottaa = 1'b0; end
    endcase
  end
endmodule
// @loppu keskeytys

module testipenkki;
  logic [7:0] kasky;
  laji_t      laji;
  logic [3:0] pyynnot;
  logic [1:0] numero;
  logic       odottaa;
  int         lajeja [6] = '{default: 0};
  int         virheita = 0;

  dekooderi         u_d (.kasky, .laji);
  keskeytysvalitsin u_k (.pyynnot, .numero, .odottaa);

  initial begin
    for (int i = 0; i < 256; i++) begin
      kasky = 8'(i);
      #1 lajeja[laji]++;
    end
    $write("lataa %0d, talleta %0d, laske %0d, ",
           lajeja[LATAA], lajeja[TALLETA], lajeja[LASKE]);
    $display("hyppy %0d, pysäytä %0d, laiton %0d",
             lajeja[HYPPY], lajeja[PYSAYTA], lajeja[LAITON]);
    kasky = 8'b1101_0110;
    #1 $display("käsky %b on %s", kasky, laji.name());

    for (int i = 0; i < 16; i++) begin
      int alin = -1;
      pyynnot = 4'(i);
      for (int b = 3; b >= 0; b--) if (pyynnot[b]) alin = b;
      #1;
      if (odottaa != (i != 0) || (odottaa && int'(numero) != alin))
        virheita++;
    end
    pyynnot = 4'b1100;
    #1 $display("pyynnöt %b: keskeytys %0d, virheitä %0d",
                pyynnot, numero, virheita);
    if (virheita != 0) $fatal(1, "valitsin toimii väärin");
  end
endmodule
