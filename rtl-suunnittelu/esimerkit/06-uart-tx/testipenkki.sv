// Testipenkki lähettää merkkijonon ja purkaa linjan kuin vastaanotin:
// odottaa aloitusbitin reunaa ja näytteistää jokaisen bitin keskeltä.
module testipenkki;
  localparam int KELLO_HZ = 1_000_000;    // jakso 10 aikayksikköä
  localparam int BAUD     = 100_000;      // bitti 10 jaksoa
  localparam int BITTI    = 100;          // bittiaika aikayksikköinä

  logic       clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic [7:0] data = '0;
  logic       kelvollinen = 1'b0, valmis, tx;
  string      viesti = "RTL!", saatu = "";

  uart_tx #(.KELLO_HZ(KELLO_HZ), .BAUD(BAUD)) u_tx (
    .clk, .rst_n, .data, .kelvollinen, .valmis, .tx);

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku vastaanotin
  task automatic vastaanota(output logic [7:0] tavu);
    @(negedge tx);                        // aloitusbitin alku
    #(BITTI / 2);
    if (tx != 1'b0) $fatal(1, "aloitusbitti puuttuu");
    for (int i = 0; i < 8; i++) begin
      #(BITTI);
      tavu[i] = tx;
    end
    #(BITTI);
    if (tx != 1'b1) $fatal(1, "lopetusbitti puuttuu");
  endtask
  // @loppu vastaanotin

  initial begin
    #12 rst_n = 1'b1;
    fork
      // @alku lahetys
      for (int i = 0; i < viesti.len(); i++) begin
        data        = viesti[i];
        kelvollinen = 1'b1;
        do @(posedge clk); while (!valmis);   // siirto tällä reunalla
        #1 kelvollinen = 1'b0;
      end
      // @loppu lahetys
      for (int i = 0; i < viesti.len(); i++) begin
        logic [7:0] tavu;
        vastaanota(tavu);
        saatu = {saatu, string'(tavu)};
      end
    join
    wait (valmis);                        // lopetusbitti loppuun
    $display("lähetetty \"%s\", vastaanotettu \"%s\"", viesti, saatu);
    $display("valmis = %b, tx = %b (lepotila)", valmis, tx);
    if (saatu != viesti) $fatal(1, "viesti vääristyi");
    kaynnissa = 1'b0;
  end
endmodule
