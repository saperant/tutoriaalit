// Siirrin multiplekserikerroksina ja kertoja summainriveinä.

// @alku siirrin
// Vasemmalle siirtävä siirrin (barrel shifter). Siirtomäärän jokainen
// bitti ohjaa yhtä multiplekserikerrosta: kerros k siirtää 2^k bittiä
// tai päästää sanan läpi. Kahdeksan bitin sanalle riittää kolme
// kerrosta, ja viive on sama kaikilla siirtomäärillä.
module siirrin8 (
  input  logic [7:0] a,
  input  logic [2:0] maara,
  output logic [7:0] y
);
  logic [7:0] k0, k1;
  assign k0 = maara[0] ? {a[6:0],  1'b0} : a;
  assign k1 = maara[1] ? {k0[5:0], 2'b0} : k0;
  assign y  = maara[2] ? {k1[3:0], 4'b0} : k1;
endmodule
// @loppu siirrin

// @alku kertoja
// Taulukkokertoja: jokainen b:n bitti valitsee AND-porteilla, otetaanko
// siirretty a mukaan (osatulo), ja osatulot lasketaan yhteen rivi
// kerrallaan. Neljän bitin kertojassa on 16 AND-porttia ja kolme
// summainriviä.
module kertoja4 (
  input  logic [3:0] a,
  input  logic [3:0] b,
  output logic [7:0] tulo
);
  logic [7:0] osatulo [4];
  always_comb begin
    for (int i = 0; i < 4; i++)
      osatulo[i] = {4'b0, a & {4{b[i]}}} << i;
    tulo = osatulo[0] + osatulo[1] + osatulo[2] + osatulo[3];
  end
endmodule
// @loppu kertoja

// @alku testipenkki
module testipenkki;
  logic [7:0] a8, y, tulo;
  logic [3:0] a4, b4;
  logic [2:0] maara;
  int         kokeita = 0, virheita = 0;

  siirrin8 u_siirrin (.a(a8), .maara, .y);
  kertoja4 u_kertoja (.a(a4), .b(b4), .tulo);

  initial begin
    for (int i = 0; i < 2048; i++) begin        // 8 + 3 bittiä
      {maara, a8} = 11'(i);
      #1 kokeita++;
      if (y != 8'(a8 << maara)) virheita++;
    end
    for (int i = 0; i < 256; i++) begin         // 4 + 4 bittiä
      {a4, b4} = 8'(i);
      #1 kokeita++;
      if (tulo != 8'(a4) * 8'(b4)) virheita++;
    end
    a8 = 8'b0000_0101; maara = 3'd3;
    #1 $display("00000101 << 3 = %b", y);
    a4 = 4'd13; b4 = 4'd11;
    #1 $display("13 * 11 = %0d", tulo);
    $display("%0d tarkistusta, %0d virhettä", kokeita, virheita);
    if (virheita != 0) $fatal(1, "siirrin tai kertoja on väärin");
  end
endmodule
// @loppu testipenkki
