// @alku mac
// Kertolasku-summa y = a * b + c kaksivaiheisena liukuhihnana.
// Jokaisella vaiheella on kelvollisuusbitti, joka kulkee datan rinnalla.
// Latenssi 2 jaksoa, läpäisy yksi tulos jaksossa.
module kerro_summaa #(parameter int W = 16) (
  input  logic           clk,
  input  logic           rst_n,
  input  logic           sisaan_kelv,
  input  logic [W-1:0]   a, b,
  input  logic [2*W-1:0] c,
  output logic           ulos_kelv,
  output logic [2*W:0]   y
);
  // Vaihe 1: kertolasku. c kulkee mukana, jotta se pysyy tahdissa.
  logic           v1;
  logic [2*W-1:0] tulo1, c1;
  // Vaihe 2: summa.
  logic           v2;
  logic [2*W:0]   summa2;

  // Kelvollisuusbitit tarvitsevat nollauksen, data ei.
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) {v1, v2} <= '0;
    else        {v1, v2} <= {sisaan_kelv, v1};
  end

  always_ff @(posedge clk) begin
    if (sisaan_kelv) begin
      tulo1 <= a * b;
      c1    <= c;
    end
    if (v1) summa2 <= tulo1 + c1;      // laajennus 2*W+1 bittiin
  end

  assign ulos_kelv = v2;
  assign y         = summa2;
endmodule
// @loppu mac

module testipenkki;
  localparam int W = 16;
  logic           clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic           sisaan_kelv = 1'b0, ulos_kelv;
  logic [W-1:0]   a = '0, b = '0;
  logic [2*W-1:0] c = '0;
  logic [2*W:0]   y;
  logic [2*W:0]   odotetut[$];
  logic [15:0]    lfsr = 16'hACE1;     // näennäissatunnainen syöte
  int             tuloksia = 0, virheita = 0;

  kerro_summaa #(.W(W)) u_mac (.clk, .rst_n, .sisaan_kelv, .a, .b, .c,
                               .ulos_kelv, .y);

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku tarkistin
  // Malli: odotettu tulos jonoon sisääntulossa, vertailu ulostulossa.
  always @(posedge clk) begin
    if (sisaan_kelv) odotetut.push_back((2*W+1)'(a * b) + (2*W+1)'(c));
    if (ulos_kelv) begin
      if (odotetut.size() == 0 || y != odotetut.pop_front())
        virheita <= virheita + 1;
      tuloksia <= tuloksia + 1;
    end
  end
  // @loppu tarkistin

  initial begin
    #12 rst_n = 1'b1;
    @(posedge clk); #1;
    for (int i = 0; i < 100; i++) begin
      lfsr        = {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
      sisaan_kelv = (lfsr[1:0] != 2'b00);   // välillä tauko
      a           = lfsr;
      b           = ~lfsr;
      c           = {lfsr, lfsr};
      if (i == 0) begin
        sisaan_kelv = 1'b1;
        a = '1; b = '1; c = '1;             // suurin mahdollinen
      end
      @(posedge clk); #1;
    end
    sisaan_kelv = 1'b0;
    repeat (3) @(posedge clk);
    #1;
    $display("tuloksia %0d, virheitä %0d, jonoon jäi %0d", tuloksia,
             virheita, odotetut.size());
    if (virheita != 0 || odotetut.size() != 0) $fatal(1, "MAC väärin");
    kaynnissa = 1'b0;
  end
endmodule
