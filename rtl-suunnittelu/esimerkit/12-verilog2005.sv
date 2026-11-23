// @alku v2005
// Sekvenssintunnistin Verilog-2005:llä: pulssi, kun bittivirrassa
// esiintyy 1011 (päällekkäiset osumat sallittu). Tilat ovat
// localparam-vakioita, rekisterit reg-tyyppiä ja kombinaatiologiikka
// always @*-lohkossa.
module tunnistin_v2005 (
  input  wire clk,
  input  wire rst_n,
  input  wire bitti,
  output reg  osuma
);
  localparam [2:0] S0 = 3'd0, S1 = 3'd1, S10 = 3'd2, S101 = 3'd3,
                   S1011 = 3'd4;
  reg [2:0] tila, seuraava;

  always @(posedge clk or negedge rst_n)
    if (!rst_n) tila <= S0;
    else        tila <= seuraava;

  always @* begin
    seuraava = tila;
    case (tila)
      S0:      seuraava = bitti ? S1    : S0;
      S1:      seuraava = bitti ? S1    : S10;
      S10:     seuraava = bitti ? S101  : S0;
      S101:    seuraava = bitti ? S1011 : S10;
      S1011:   seuraava = bitti ? S1    : S10;
      default: seuraava = S0;
    endcase
  end

  always @* osuma = (tila == S1011);
endmodule
// @loppu v2005

// @alku sv
// Sama SystemVerilogilla: enum, always_ff, always_comb ja unique case.
module tunnistin_sv (
  input  logic clk,
  input  logic rst_n,
  input  logic bitti,
  output logic osuma
);
  typedef enum logic [2:0] {S0, S1, S10, S101, S1011} tila_t;
  tila_t tila, seuraava;

  always_ff @(posedge clk or negedge rst_n)
    if (!rst_n) tila <= S0;
    else        tila <= seuraava;

  always_comb begin
    unique case (tila)
      S0:      seuraava = bitti ? S1    : S0;
      S1:      seuraava = bitti ? S1    : S10;
      S10:     seuraava = bitti ? S101  : S0;
      S101:    seuraava = bitti ? S1011 : S10;
      S1011:   seuraava = bitti ? S1    : S10;
      default: seuraava = S0;           // 3 bittiä, 5 tilaa
    endcase
  end

  assign osuma = (tila == S1011);
endmodule
// @loppu sv

module testipenkki;
  logic        clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0, bitti = 1'b0;
  logic        osuma_v, osuma_s;
  logic [15:0] virta = 16'b1011_0110_1101_1000;
  int          osumia = 0, eroja = 0;

  tunnistin_v2005 u_v (.clk, .rst_n, .bitti, .osuma(osuma_v));
  tunnistin_sv    u_s (.clk, .rst_n, .bitti, .osuma(osuma_s));

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    #12 rst_n = 1'b1;
    for (int i = 15; i >= 0; i--) begin   // eniten merkitsevä ensin
      bitti = virta[i];
      @(posedge clk); #1;
      if (osuma_v) osumia++;
      if (osuma_v != osuma_s) eroja++;
    end
    $display("virta %b: %0d osumaa, versioiden eroja %0d", virta,
             osumia, eroja);
    if (osumia != 4 || eroja != 0) $fatal(1, "tunnistin väärin");
    kaynnissa = 1'b0;
  end
endmodule
