// Sisäänrakennettu itsetestaus (BIST): LFSR tuottaa näennäis-
// satunnaiset testivektorit ja MISR tiivistää vasteet allekirjoitukseksi.
// Testattava lohko on 4×4-kertoja; toiseen kopioon on istutettu
// juuttumisvika.

// @alku lfsr
// 8-bittinen Galois-LFSR, polynomi x^8 + x^6 + x^5 + x^4 + 1:
// käy läpi kaikki 255 nollasta poikkeavaa tilaa.
module lfsr (input logic clk, nollaa, output logic [7:0] tila);
  always_ff @(posedge clk)
    if (nollaa) tila <= 8'h01;
    else        tila <= {1'b0, tila[7:1]} ^ (tila[0] ? 8'hB8 : 8'h00);
endmodule
// @loppu lfsr

// @alku misr
// MISR: LFSR, johon testattavan lohkon lähdöt XOR:ataan joka jaksolla.
module misr (input logic clk, nollaa, input logic [7:0] vaste,
             output logic [7:0] allekirjoitus);
  always_ff @(posedge clk)
    if (nollaa) allekirjoitus <= 8'h00;
    else allekirjoitus <= ({1'b0, allekirjoitus[7:1]}
                           ^ (allekirjoitus[0] ? 8'hB8 : 8'h00)) ^ vaste;
endmodule
// @loppu misr

// Testattava lohko; VIKA=1 juuttaa tulon a bitin 2 nollaan.
module kertoja4 #(parameter bit VIKA = 0)
  (input logic [3:0] a, b, output logic [7:0] p);
  logic [3:0] a_sisalla;
  assign a_sisalla = VIKA ? (a & 4'b1011) : a;
  assign p = a_sisalla * b;
endmodule

// @alku testipenkki
module testipenkki;
  logic clk = 1'b0, kaynnissa = 1'b1, nollaa = 1'b1;
  logic [7:0] vektori, p_ehja, p_vika, sig_ehja, sig_vika;

  lfsr          u_l  (.clk, .nollaa, .tila(vektori));
  kertoja4      u_e  (.a(vektori[7:4]), .b(vektori[3:0]), .p(p_ehja));
  kertoja4 #(1) u_v  (.a(vektori[7:4]), .b(vektori[3:0]), .p(p_vika));
  misr          u_me (.clk, .nollaa, .vaste(p_ehja),
                      .allekirjoitus(sig_ehja));
  misr          u_mv (.clk, .nollaa, .vaste(p_vika),
                      .allekirjoitus(sig_vika));

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    @(posedge clk); #1 nollaa = 1'b0;
    repeat (255) @(posedge clk);
    #1;
    $display("255 vektoria: allekirjoitus ehjä %h, viallinen %h",
             sig_ehja, sig_vika);
    $display("vika havaittu: %s", sig_ehja != sig_vika ? "kyllä" : "ei");
    kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
