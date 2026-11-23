// Käy läpi kaikki 4-bittisen summaimen syötteet ja vertaa malliin.
module testipenkki;
  localparam int N = 4;

  logic [N-1:0] a, b, summa;
  logic         cin, cout;
  int           tapauksia = 0;
  int           virheita = 0;

  summain #(.N(N)) dut (
    .a, .b, .muistibitti_sisaan(cin), .summa, .muistibitti_ulos(cout)
  );

  initial begin
    for (int i = 0; i < 2 ** (2 * N + 1); i++) begin
      {cin, a, b} = (2 * N + 1)'(i);
      #1;
      if ({cout, summa} != {1'b0, a} + {1'b0, b} + (N + 1)'(cin)) begin
        virheita++;
        $display("VIRHE: %0d + %0d + %0d = %0d", a, b, cin, {cout, summa});
      end
      tapauksia++;
    end
    $display("%0d tapausta, %0d virhettä", tapauksia, virheita);
    if (virheita != 0) $fatal(1, "summain laskee väärin");
  end
endmodule
