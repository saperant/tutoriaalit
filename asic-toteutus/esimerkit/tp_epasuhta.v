// Testipenkki epasuhta-moduulille: b muuttuu, kun a pysyy ennallaan.
`timescale 1ns/1ps
module tp;
  reg a = 0, b = 0;
  wire y;
  epasuhta dut (.a(a), .b(b), .y(y));
  initial begin
    #1 a = 1;  #1 $display("a=1 b=0: y=%b", y);
    #1 b = 1;  #1 $display("a=1 b=1: y=%b", y);
    $finish;
  end
endmodule
