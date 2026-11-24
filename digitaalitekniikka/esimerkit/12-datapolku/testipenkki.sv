// @alku testipenkki
module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1, nollaa = 1'b1;
  logic [3:0] pc;
  logic [1:0] rd;
  logic [7:0] tulos;
  string      fibonacci = "";

  datapolku dut (.clk, .nollaa, .pc, .rd, .tulos);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    @(posedge clk); #1 nollaa = 1'b0;
    repeat (16) begin
      #3;                           // tulos on valmis ennen reunaa
      if (pc < 4'd6) $display("pc=%2d  r%0d <= %0d", pc, rd, tulos);
      if (rd == 2'd2) fibonacci = {fibonacci, $sformatf(" %0d", tulos)};
      @(posedge clk); #1;
    end
    $display("...");
    $display("r2:n arvot:%s", fibonacci);
    if (fibonacci != " 1 2 3 5 8") $fatal(1, "datapolku laskee väärin");
    kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
