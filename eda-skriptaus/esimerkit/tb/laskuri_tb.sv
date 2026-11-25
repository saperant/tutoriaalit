// Laskurin pieni testipenkki, joka tallentaa aaltomuodot VCD-tiedostoon.
// Tulosta ei tarkisteta täällä: sen tekee Python VCD:stä (05-vcd.py).
`timescale 1ns/1ps
module laskuri_tb;
  logic       clk = 1'b0;
  logic       rst_n = 1'b0;
  logic       sallittu = 1'b0;
  logic [2:0] arvo;
  logic       yli;

  laskuri #(.LEVEYS(3)) dut (.*);

  always #5 clk = ~clk;

  initial begin
    string tiedosto;
    if (!$value$plusargs("vcd=%s", tiedosto)) tiedosto = "laskuri.vcd";
    $dumpfile(tiedosto);
    $dumpvars(0, laskuri_tb);
    repeat (2) @(negedge clk);
    rst_n = 1'b1;
    @(negedge clk) sallittu = 1'b1;
    repeat (5) @(negedge clk);
    sallittu = 1'b0;                 // tauko: arvo pysyy
    repeat (2) @(negedge clk);
    sallittu = 1'b1;
    repeat (5) @(negedge clk);       // ylivuoto 7 -> 0
    $finish;
  end
endmodule
