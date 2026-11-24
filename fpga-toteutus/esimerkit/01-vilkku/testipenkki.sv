// Testipenkki: lyhyt laskuri, jotta ledin vaihtuminen näkyy nopeasti.
module testipenkki;
  logic clk = 1'b0;
  logic kaynnissa = 1'b1;
  logic led_n;
  int   vaihdot = 0;

  vilkku #(.BITIT(3)) dut (.clk, .led_n);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    logic edellinen;
    edellinen = 1'b1;
    for (int jakso = 1; jakso <= 24; jakso++) begin
      @(posedge clk); #1;
      if (led_n != edellinen) begin
        $display("jakso %2d: led %s", jakso, led_n ? "sammui" : "syttyi");
        vaihdot++;
        edellinen = led_n;
      end
    end
    if (vaihdot != 6) $fatal(1, "ledi vaihtui %0d kertaa", vaihdot);
    kaynnissa = 1'b0;
  end
endmodule
