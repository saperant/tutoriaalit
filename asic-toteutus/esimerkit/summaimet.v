// Kolme 32-bittistä summainta samoilla rekistereillä. Arkkitehtuuri on
// kirjoitettu RTL:ään, koska optimoija ei vaihda sitä toiseksi.

// @alku ripple
// Ripple-carry: muistibitti kulkee täyssummainketjun läpi.
module summain_ripple (
  input  wire        clk,
  input  wire [31:0] a, b,
  output reg  [31:0] s
);
  reg  [31:0] a_r, b_r;
  wire [32:0] c;
  wire [31:0] summa;
  assign c[0] = 1'b0;
  genvar i;
  generate for (i = 0; i < 32; i = i + 1) begin : fa
    assign summa[i] = a_r[i] ^ b_r[i] ^ c[i];
    assign c[i+1]   = (a_r[i] & b_r[i]) | (c[i] & (a_r[i] ^ b_r[i]));
  end endgenerate
  always @(posedge clk) begin
    a_r <= a; b_r <= b; s <= summa;
  end
endmodule
// @loppu ripple

// @alku bk
// Yosysin oletus: + kuvataan Brent–Kung-etuliiteverkoksi.
module summain_bk (
  input  wire        clk,
  input  wire [31:0] a, b,
  output reg  [31:0] s
);
  reg [31:0] a_r, b_r;
  always @(posedge clk) begin
    a_r <= a; b_r <= b; s <= a_r + b_r;
  end
endmodule
// @loppu bk

// @alku ks
// Kogge–Stone: log2(32) = 5 tasoa, jokaisella tasolla täysi rivi
// generoi–propagoi-soluja.
module summain_ks (
  input  wire        clk,
  input  wire [31:0] a, b,
  output reg  [31:0] s
);
  reg  [31:0] a_r, b_r;
  wire [31:0] g [0:5];
  wire [31:0] p [0:5];
  assign g[0] = a_r & b_r;
  assign p[0] = a_r ^ b_r;
  genvar t, j;
  generate for (t = 0; t < 5; t = t + 1) begin : taso
    for (j = 0; j < 32; j = j + 1) begin : solu
      if (j >= (1 << t)) begin : yhdista
        assign g[t+1][j] = g[t][j] | (p[t][j] & g[t][j - (1 << t)]);
        assign p[t+1][j] = p[t][j] & p[t][j - (1 << t)];
      end else begin : lapi
        assign g[t+1][j] = g[t][j];
        assign p[t+1][j] = p[t][j];
      end
    end
  end endgenerate
  always @(posedge clk) begin
    a_r <= a; b_r <= b; s <= p[0] ^ {g[5][30:0], 1'b0};
  end
endmodule
// @loppu ks
