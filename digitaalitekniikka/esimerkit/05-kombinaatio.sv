// Kombinaatiologiikan peruslohkot ja niiden tyhjentävä testaus.

// @alku mux
// Neljän syötteen multiplekseri: valinta s ohjaa yhden syötteen lähtöön.
module mux4 (
  input  logic [3:0] d,
  input  logic [1:0] s,
  output logic       y
);
  assign y = d[s];
endmodule
// @loppu mux

// @alku dekooderi
// 2→4-dekooderi: täsmälleen yksi lähtö on 1, kun sallinta on päällä.
module dekooderi (
  input  logic [1:0] a,
  input  logic       sallinta,
  output logic [3:0] y
);
  assign y = sallinta ? 4'b0001 << a : 4'b0000;
endmodule
// @loppu dekooderi

// @alku prioriteetti
// Prioriteettikooderi: suurimman ykkösen indeksi ja tieto, oliko
// yhtään ykköstä.
module prioriteetti (
  input  logic [3:0] pyynto,
  output logic [1:0] indeksi,
  output logic       kelvollinen
);
  always_comb begin
    indeksi     = 2'd0;          // oletusarvot ensin
    kelvollinen = 1'b1;
    if      (pyynto[3]) indeksi = 2'd3;
    else if (pyynto[2]) indeksi = 2'd2;
    else if (pyynto[1]) indeksi = 2'd1;
    else if (pyynto[0]) indeksi = 2'd0;
    else                kelvollinen = 1'b0;
  end
endmodule
// @loppu prioriteetti

// @alku vertailija
// Neljän bitin vertailija bitti kerrallaan eniten merkitsevästä alkaen.
module vertailija (
  input  logic [3:0] a,
  input  logic [3:0] b,
  output logic       pienempi,
  output logic       yhtasuuri
);
  always_comb begin
    pienempi  = 1'b0;
    yhtasuuri = 1'b1;
    for (int i = 3; i >= 0; i--) begin
      if (yhtasuuri && a[i] != b[i]) begin
        pienempi  = b[i];        // ensimmäinen eroava bitti ratkaisee
        yhtasuuri = 1'b0;
      end
    end
  end
endmodule
// @loppu vertailija

// @alku testipenkki
module testipenkki;
  logic [3:0] d, a4, b4, dek, pyynto;
  logic [1:0] s, a2, indeksi;
  logic       y, sallinta, kelvollinen, pienempi, yhtasuuri;
  int         kokeita = 0, virheita = 0;

  mux4         u_mux (.d, .s, .y);
  dekooderi    u_dek (.a(a2), .sallinta, .y(dek));
  prioriteetti u_pri (.pyynto, .indeksi, .kelvollinen);
  vertailija   u_ver (.a(a4), .b(b4), .pienempi, .yhtasuuri);

  task automatic tarkista(logic ehto, string mika);
    kokeita++;
    if (!ehto) begin
      virheita++;
      $display("VIRHE: %s", mika);
    end
  endtask

  initial begin
    // Kaikki syötekombinaatiot: logiikka on pieni, joten tyhjentävä
    // testaus on mahdollinen ja paras.
    for (int i = 0; i < 64; i++) begin
      {s, d} = 6'(i);
      #1 tarkista(y == d[s], "mux4");
    end
    for (int i = 0; i < 8; i++) begin
      {sallinta, a2} = 3'(i);
      #1 tarkista(dek == (sallinta ? 4'(1 << a2) : 4'b0), "dekooderi");
      tarkista($countones(dek) == (sallinta ? 1 : 0), "yksi kuuma");
    end
    for (int i = 0; i < 16; i++) begin
      pyynto = 4'(i);
      #1 tarkista(kelvollinen == (i != 0), "kelvollinen");
      if (i != 0) tarkista(int'(indeksi) == $clog2(i + 1) - 1,
                           "prioriteetti");
    end
    for (int i = 0; i < 256; i++) begin
      {a4, b4} = 8'(i);
      #1 tarkista(pienempi == (a4 < b4) && yhtasuuri == (a4 == b4),
                  "vertailija");
    end
    $display("%0d tarkistusta, %0d virhettä", kokeita, virheita);
    if (virheita != 0) $fatal(1, "kombinaatiologiikka on väärin");
  end
endmodule
// @loppu testipenkki
