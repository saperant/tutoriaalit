// Itsetarkistava testipenkki: satunnaiset operaatiot omalla
// xorshift-generaattorilla, joten tulos riippuu vain siemenestä.
// Plusargit: +siemen=N, +maara=N, +jumita (testaa aikakatkaisua).
// Lopuksi tulostetaan toiminnallisen kattavuuden lokerot: operaatio ja
// operandien ylimmät bitit (4 x 2 x 2 = 16 lokeroa).
module alu_tb;
  logic [1:0] op;
  logic [7:0] a, b, y, odotettu;
  int unsigned tila, maara, virheet;
  int unsigned osumat[4][2][2];

  alu dut (.op, .a, .b, .y);

  // @alku siemen
  function automatic int unsigned seuraava();
    tila ^= tila << 13;
    tila ^= tila >> 17;
    tila ^= tila << 5;
    return tila;
  endfunction

  initial begin
    if (!$value$plusargs("siemen=%d", tila)) tila = 1;
    if (tila == 0) tila = 1;
    if (!$value$plusargs("maara=%d", maara)) maara = 200;
    if ($test$plusargs("jumita")) forever #1;
    // @loppu siemen
    virheet = 0;
    for (int i = 0; i < maara; i++) begin
      op = 2'(seuraava());
      a = 8'(seuraava());
      b = 8'(seuraava());
      #1;
      osumat[op][a[7]][b[7]]++;
      unique case (op)
        2'd0: odotettu = a + b;
        2'd1: odotettu = a - b;
        2'd2: odotettu = a & b;
        default: odotettu = a ^ b;
      endcase
      if (y !== odotettu) begin
        virheet++;
        if (virheet <= 3)
          $display("VIRHE op=%0d a=%0d b=%0d saatu=%0d odotettu=%0d",
                   op, a, b, y, odotettu);
      end
    end
    for (int o = 0; o < 4; o++)
      for (int i = 0; i < 2; i++)
        for (int j = 0; j < 2; j++)
          $display("KATTAVUUS op=%0d a7=%0d b7=%0d osumia=%0d",
                   o, i, j, osumat[o][i][j]);
    if (virheet == 0) $display("TESTI OK %0d operaatiota", maara);
    else $display("TESTI EPÄONNISTUI %0d virhettä", virheet);
    $finish;
  end
endmodule
