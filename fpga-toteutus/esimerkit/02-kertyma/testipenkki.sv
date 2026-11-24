// Testipenkki: summataan 1, 2, ..., 300; summa pyörähtää 16 bitissä.
module testipenkki;
  logic        clk = 1'b0;
  logic        kaynnissa = 1'b1;
  logic        tyhjenna = 1'b1;
  logic [7:0]  x = '0;
  logic [15:0] summa;
  int          odotettu = 0;

  kertyma dut (.clk, .tyhjenna, .x, .summa);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    @(posedge clk); #1 tyhjenna = 1'b0;
    // @alku tarkistus
    for (int i = 1; i <= 300; i++) begin
      x = 8'(i);
      odotettu = (odotettu + (i % 256)) % 65536;
      @(posedge clk); #1;
      if (summa != 16'(odotettu)) $fatal(1, "summa väärin kohdassa %0d", i);
    end
    // @loppu tarkistus
    $display("summa 300 jakson jälkeen: %0d", summa);
    kaynnissa = 1'b0;
  end
endmodule
