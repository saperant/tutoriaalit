// @alku moduuli
// Ylöspäin laskeva laskuri, jolla on sallintasignaali.
module laskuri #(
  parameter int LEVEYS = 4
) (
  input  logic              clk,
  input  logic              rst_n,   // asynkroninen, aktiivinen alhaalla
  input  logic              sallittu,
  output logic [LEVEYS-1:0] arvo
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      arvo <= '0;
    end else if (sallittu) begin
      arvo <= arvo + 1'b1;
    end
  end
endmodule
// @loppu moduuli

// @alku testipenkki
module testipenkki;
  logic       clk = 1'b0;
  logic       kaynnissa = 1'b1;
  logic       rst_n = 1'b0;
  logic       sallittu = 1'b0;
  logic [3:0] arvo;

  laskuri #(.LEVEYS(4)) dut (.clk, .rst_n, .sallittu, .arvo);

  // Kello: jakso 10 aikayksikköä niin kauan kuin testi on käynnissä.
  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    #12 rst_n = 1'b1;           // reset vapautuu kellojen välissä
    @(posedge clk); #1;
    sallittu = 1'b1;
    repeat (3) @(posedge clk);
    #1 $display("3 jaksoa: arvo = %0d", arvo);

    sallittu = 1'b0;
    repeat (2) @(posedge clk);
    #1 $display("pysäytetty: arvo = %0d", arvo);

    sallittu = 1'b1;
    repeat (14) @(posedge clk);
    #1 $display("17 jaksoa: arvo = %0d (4 bittiä pyörähtää)", arvo);
    if (arvo != 4'd1) $fatal(1, "laskurin arvo on väärä");
    kaynnissa = 1'b0;           // kello pysähtyy, simulaatio päättyy
  end
endmodule
// @loppu testipenkki
