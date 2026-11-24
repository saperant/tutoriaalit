// Testipenkki: nollauksen vapautuminen kahden jakson viiveellä.
module testipenkki;
  logic clk_12 = 1'b0;
  logic kaynnissa = 1'b1;
  logic led_n;

  pll_ylin dut (.clk_12, .led_n);

  initial while (kaynnissa) #5 clk_12 = ~clk_12;

  initial begin
    for (int jakso = 1; jakso <= 4; jakso++) begin
      @(posedge clk_12); #1;
      $display("jakso %0d: nollaus=%b laskuri=%0d led_n=%b", jakso,
               dut.nollaus, dut.laskuri, led_n);
    end
    kaynnissa = 1'b0;
  end
endmodule
