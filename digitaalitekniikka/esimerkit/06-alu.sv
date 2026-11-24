// Neljän bitin ALU ja sen tilaliput N, Z, C ja V.

// @alku alu
module alu4 (
  input  logic [2:0] op,        // 0 ADD, 1 SUB, 2 AND, 3 OR, 4 XOR
  input  logic [3:0] a,
  input  logic [3:0] b,
  output logic [3:0] y,
  output logic       n,         // tulos negatiivinen (MSB)
  output logic       z,         // tulos nolla
  output logic       c,         // muistibitti ulos
  output logic       v          // etumerkillinen ylivuoto
);
  // Vähennys on yhteenlasku: a - b = a + ~b + 1. Sama summain riittää,
  // kun b käännetään ja tulomuistiksi annetaan 1.
  logic       vahenna;
  logic [3:0] bb;
  logic [3:0] summa;
  logic       c_msb, c_ulos;    // muistibitti MSB:hen ja siitä ulos

  assign vahenna = (op == 3'd1);
  assign bb      = vahenna ? ~b : b;

  // Ripple-carry silmukkana: muuttuja m on muistibitti bitistä toiseen.
  always_comb begin
    logic m;
    m     = vahenna;
    c_msb = 1'b0;
    for (int i = 0; i < 4; i++) begin
      if (i == 3) c_msb = m;
      summa[i] = a[i] ^ bb[i] ^ m;
      m        = (a[i] & bb[i]) | ((a[i] ^ bb[i]) & m);
    end
    c_ulos = m;
  end

  always_comb begin
    c = 1'b0;                   // liput vain aritmeettisista käskyistä
    v = 1'b0;
    case (op)
      3'd0, 3'd1: begin
        y = summa;
        c = c_ulos;
        v = c_ulos ^ c_msb;     // muisti MSB:hen ≠ muisti MSB:stä
      end
      3'd2:    y = a & b;
      3'd3:    y = a | b;
      3'd4:    y = a ^ b;
      default: y = 4'b0;
    endcase
  end

  assign n = y[3];
  assign z = (y == 4'b0);
endmodule
// @loppu alu

// @alku testipenkki
module testipenkki;
  logic [2:0] op;
  logic [3:0] a, b, y;
  logic       n, z, c, v;
  int         virheita = 0;

  alu4 dut (.op, .a, .b, .y, .n, .z, .c, .v);

  // Viitemalli lasketaan eri tavalla: kokonaislukuina.
  function automatic logic [3:0] viite_y(int o, int x, int w);
    case (o)
      0: return 4'(x + w);
      1: return 4'(x - w);
      2: return 4'(x & w);
      3: return 4'(x | w);
      default: return 4'(x ^ w);
    endcase
  endfunction

  function automatic int etumerkillinen(logic [3:0] x);
    return x[3] ? int'(x) - 16 : int'(x);
  endfunction

  initial begin
    for (int o = 0; o < 5; o++) begin
      for (int i = 0; i < 256; i++) begin
        op = 3'(o);
        {a, b} = 8'(i);
        #1;
        if (y != viite_y(o, int'(a), int'(b))) virheita++;
        if (o == 0 && (c != (int'(a) + int'(b) > 15) ||
            v != (etumerkillinen(a) + etumerkillinen(b) > 7 ||
                  etumerkillinen(a) + etumerkillinen(b) < -8)))
          virheita++;
        if (o == 1 && (c != (int'(a) >= int'(b)) ||
            v != (etumerkillinen(a) - etumerkillinen(b) > 7 ||
                  etumerkillinen(a) - etumerkillinen(b) < -8)))
          virheita++;
      end
    end
    // Esimerkkejä lipuista.
    op = 3'd0; a = 4'd7; b = 4'd1; #1;
    $display("7 + 1:   y=%b  N=%b Z=%b C=%b V=%b", y, n, z, c, v);
    op = 3'd0; a = 4'hF; b = 4'd1; #1;
    $display("-1 + 1:  y=%b  N=%b Z=%b C=%b V=%b", y, n, z, c, v);
    op = 3'd1; a = 4'd3; b = 4'd5; #1;
    $display("3 - 5:   y=%b  N=%b Z=%b C=%b V=%b", y, n, z, c, v);
    op = 3'd1; a = 4'h8; b = 4'd1; #1;
    $display("-8 - 1:  y=%b  N=%b Z=%b C=%b V=%b", y, n, z, c, v);
    $display("1280 tapausta, %0d virhettä", virheita);
    if (virheita != 0) $fatal(1, "ALU laskee väärin");
  end
endmodule
// @loppu testipenkki
