// @alku testipenkki
// Molemmat summaimet testataan kaikilla 8-bittisillä syötteillä ja
// muistibitillä: 2 · 256 · 256 = 131 072 tapausta.
module testipenkki;
  logic [7:0] a, b, s_rca, s_cla;
  logic       cin, cout_rca, cout_cla, c_vali;
  int         virheita = 0;

  rca #(.N(8)) u_rca (.a, .b, .cin, .s(s_rca), .cout(cout_rca));

  // Kahdeksan bittiä kahdesta CLA-lohkosta, joiden välillä muistibitti
  // kulkee ketjuna.
  cla4 u_ala (.a(a[3:0]), .b(b[3:0]), .cin,
              .s(s_cla[3:0]), .cout(c_vali));
  cla4 u_yla (.a(a[7:4]), .b(b[7:4]), .cin(c_vali),
              .s(s_cla[7:4]), .cout(cout_cla));

  initial begin
    for (int i = 0; i < 2 * 256 * 256; i++) begin
      {cin, a, b} = 17'(i);
      #1;
      if ({cout_rca, s_rca} != 9'(a) + 9'(b) + 9'(cin) ||
          {cout_cla, s_cla} != {cout_rca, s_rca}) begin
        virheita++;
      end
    end
    $display("131072 summaa, %0d virhettä", virheita);
    if (virheita != 0) $fatal(1, "summain laskee väärin");
  end
endmodule
// @loppu testipenkki
