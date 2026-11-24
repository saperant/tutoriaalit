// Testipenkki toimii isäntänä: lähettää komennot UARTin kautta ja lukee
// vastaukset. Bittiaika on testissä 8 kellojaksoa.
module testipenkki;
  localparam int B = 8;
  logic clk = 1'b0, kaynnissa = 1'b1, rx = 1'b1, tx, led_n;

  debug_ylin #(.KELLOT_PER_BITTI(B)) dut (.clk, .rx, .tx, .led_n);

  initial while (kaynnissa) #5 clk = ~clk;

  task automatic laheta(input logic [7:0] t);
    logic [9:0] kehys;
    kehys = {1'b1, t, 1'b0};
    for (int i = 0; i < 10; i++) begin
      rx = kehys[i];
      repeat (B) @(posedge clk);
    end
  endtask

  task automatic vastaanota(output logic [7:0] t);
    while (tx) @(posedge clk);
    repeat (B + B / 2) @(posedge clk);     // ensimmäisen databitin keskelle
    for (int i = 0; i < 8; i++) begin
      t[i] = tx;
      repeat (B) @(posedge clk);
    end
  endtask

  task automatic lue(input logic [7:0] osoite);
    logic [7:0] arvo;
    fork
      begin laheta("L"); laheta(osoite); end
      vastaanota(arvo);
    join
    $display("L %0d -> %h", osoite, arvo);
  endtask

  task automatic kirjoita(input logic [7:0] osoite, input logic [7:0] a);
    logic [7:0] kuittaus;
    fork
      begin laheta("K"); laheta(osoite); laheta(a); end
      vastaanota(kuittaus);
    join
    $display("K %0d %h -> %s, led_n=%b", osoite, a, kuittaus, led_n);
  endtask

  initial begin
    repeat (4) @(posedge clk);
    lue(8'd5);
    lue(8'd0);
    kirjoita(8'd0, 8'h01);
    kirjoita(8'd2, 8'h5A);
    lue(8'd2);
    lue(8'd0);
    kaynnissa = 1'b0;
  end
endmodule
