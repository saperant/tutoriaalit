// @alku lfsr
// Galois-LFSR, jonka takaisinkytkentä valitaan leveyden mukaan
// käännösaikana. Maksimipituinen: jakso 2**N - 1 tilaa.
module lfsr #(parameter int N = 8) (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         sallittu,
  output logic [N-1:0] tila
);
  logic [N-1:0] kytkenta;

  // generate-case valitsee vakion; laitteistoa ei synny.
  if      (N == 4) begin : g_n4 assign kytkenta = 4'h9;  end
  else if (N == 5) begin : g_n5 assign kytkenta = 5'h12; end
  else if (N == 6) begin : g_n6 assign kytkenta = 6'h21; end
  else if (N == 7) begin : g_n7 assign kytkenta = 7'h41; end
  else if (N == 8) begin : g_n8 assign kytkenta = 8'h8E; end
  else begin : g_tuntematon
    $error("lfsr: leveyttä N=%0d ei tueta", N);    // käännösvirhe
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)        tila <= N'(1);              // ei koskaan nolla
    else if (sallittu) tila <= (tila >> 1) ^ (tila[0] ? kytkenta : '0);
  end
endmodule
// @loppu lfsr

module testipenkki;
  logic clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0, mittaa = 1'b0;
  int   jaksot[4:8];

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku generate
  // Yksi LFSR kullekin leveydelle 4..8 ja jokaiselle oma mittari.
  for (genvar n = 4; n <= 8; n++) begin : g_leveys
    logic [n-1:0] tila;
    int           askelia = 0;
    lfsr #(.N(n)) u_lfsr (.clk, .rst_n, .sallittu(1'b1), .tila);
    always @(posedge clk) begin
      if (mittaa) askelia <= askelia + 1;
      if (mittaa && tila == n'(1) && askelia > 0 && jaksot[n] == 0)
        jaksot[n] <= askelia;            // ensimmäinen paluu alkuun
    end
  end
  // @loppu generate

  initial begin
    foreach (jaksot[n]) jaksot[n] = 0;
    #12 rst_n = 1'b1;
    mittaa = 1'b1;
    repeat (300) @(posedge clk);
    #1;
    foreach (jaksot[n]) begin
      $display("N = %0d: jakso %3d (2**N - 1 = %3d)", n, jaksot[n],
               (1 << n) - 1);
      if (jaksot[n] != (1 << n) - 1) $fatal(1, "ei maksimipituinen");
    end
    kaynnissa = 1'b0;
  end
endmodule
