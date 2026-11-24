// Rekisterit ja laskurit: kaikki samalla kellolla, synkroninen nollaus.

// @alku laskuri
// Binäärilaskuri, jolla on sallinta ja synkroninen nollaus.
module laskuri #(parameter int N = 4) (
  input  logic         clk,
  input  logic         nollaa,
  input  logic         sallinta,
  output logic [N-1:0] q
);
  always_ff @(posedge clk) begin
    if (nollaa)        q <= '0;
    else if (sallinta) q <= q + 1'b1;
  end
endmodule
// @loppu laskuri

// @alku siirto
// Siirtorekisteri: sarjamuotoinen syöte rinnakkaismuotoon.
module siirtorekisteri #(parameter int N = 4) (
  input  logic         clk,
  input  logic         sarja,
  output logic [N-1:0] q
);
  always_ff @(posedge clk) q <= {q[N-2:0], sarja};
endmodule
// @loppu siirto

// @alku rengas
// Rengaslaskuri kiertää yhtä ykköstä (one-hot); Johnson-laskuri
// kiertää käännettyä MSB:tä ja käy läpi 2N tilaa N kiikulla.
module rengaslaskurit #(parameter int N = 4) (
  input  logic         clk,
  input  logic         nollaa,
  output logic [N-1:0] rengas,
  output logic [N-1:0] johnson
);
  always_ff @(posedge clk) begin
    if (nollaa) begin
      rengas  <= N'(1);
      johnson <= '0;
    end else begin
      rengas  <= {rengas[N-2:0], rengas[N-1]};
      johnson <= {johnson[N-2:0], ~johnson[N-1]};
    end
  end
endmodule
// @loppu rengas

// @alku testipenkki
module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1;
  logic       nollaa = 1'b1, sallinta = 1'b1, sarja = 1'b0;
  logic [3:0] binaari, siirto, rengas, johnson;
  logic [7:0] syote = 8'b1011_0010;    // siirretään sisään MSB ensin

  laskuri         u_l (.clk, .nollaa, .sallinta, .q(binaari));
  siirtorekisteri u_s (.clk, .sarja, .q(siirto));
  rengaslaskurit  u_r (.clk, .nollaa, .rengas, .johnson);

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    @(posedge clk); #1 nollaa = 1'b0;
    $display("jakso binääri siirto rengas johnson");
    for (int j = 0; j < 9; j++) begin
      sarja = syote[7 - (j % 8)];
      $display("%5d   %b   %b   %b   %b", j, binaari, siirto, rengas,
               johnson);
      @(posedge clk); #1;
    end
    kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
