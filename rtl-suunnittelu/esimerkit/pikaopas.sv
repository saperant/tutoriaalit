// Pikaoppaan mallipohjat. Jokainen osa kääntyy ja testataan.

// @alku tyypit
typedef enum logic [1:0] {LEPO, AJO, ODOTUS} tila_t;
typedef struct packed {
  logic [7:0] osoite;
  logic [7:0] data;
} paketti_t;                        // 16 bittiä, osat nimillä
// @loppu tyypit

// @alku moduuli
module malli #(
  parameter int W = 8               // parametri: ylätaso voi muuttaa
) (
  input  logic         clk,
  input  logic         rst_n,       // asynkroninen, aktiivinen 0
  input  logic         alku,
  input  logic [W-1:0] d,
  output logic [W-1:0] q,
  output logic         valmis
);
  localparam int LW = $clog2(W);    // johdettu vakio
  // @loppu moduuli

  // @alku rekisteri
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n)      q <= '0;
    else if (alku)   q <= d;        // sallinta: muuten pitää arvon
  end
  // @loppu rekisteri

  // @alku tilakone
  tila_t         tila_q, tila_d;
  logic [LW-1:0] laskuri;

  always_comb begin
    tila_d = tila_q;                // oletus ensin: ei salpoja
    valmis = 1'b0;
    unique case (tila_q)
      LEPO:    if (alku) tila_d = AJO;
      AJO:     if (laskuri == '1) tila_d = ODOTUS;
      ODOTUS:  begin valmis = 1'b1; tila_d = LEPO; end
      default: tila_d = LEPO;
    endcase
  end

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      tila_q  <= LEPO;
      laskuri <= '0;
    end else begin
      tila_q  <= tila_d;
      laskuri <= (tila_q == AJO) ? laskuri + 1'b1 : '0;
    end
  end
  // @loppu tilakone
endmodule

module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0, alku = 1'b0;
  logic [7:0] d = 8'h3C, q;
  logic       valmis;
  paketti_t   p;
  int         jaksoja = 0;

  malli #(.W(8)) u_malli (.clk, .rst_n, .alku, .d, .q, .valmis);

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku testipenkki
  initial begin
    #12 rst_n = 1'b1;               // nollaus pois kesken jakson
    @(posedge clk); #1;             // syötteet reunan jälkeen
    alku = 1'b1;
    @(posedge clk); #1;
    alku = 1'b0;
    while (!valmis) begin
      @(posedge clk); #1;
      jaksoja++;
    end
    p = '{osoite: 8'h10, data: q};
    $display("q = %h, valmis %0d jakson jälkeen, paketti %h", q,
             jaksoja, p);
    if (q != 8'h3C) $fatal(1, "q väärin");
    kaynnissa = 1'b0;               // kello seis: simulaatio päättyy
  end
  // @loppu testipenkki
endmodule
