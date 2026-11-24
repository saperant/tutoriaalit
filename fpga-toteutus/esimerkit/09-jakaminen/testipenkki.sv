// Testipenkki: impulssi ja askel molempiin versioihin. Jaettu versio
// tarvitsee viisi jaksoa näytettä kohden, joten näytteitä syötetään
// valmis-signaalin tahdissa.
module testipenkki;
  logic        clk = 1'b0, kaynnissa = 1'b1, nollaus = 1'b1;
  logic        x_kelpaa = 1'b0, k_kirjoita = 1'b0;
  logic [1:0]  k_osoite = '0;
  logic [7:0]  x = '0;
  logic        valmis_r, valmis_j, kelpaa_r, kelpaa_j;
  logic [17:0] y_r, y_j;
  int          jaksot = 0;

  suodin #(.RINNAKKAIN(1'b1)) r (.clk, .nollaus, .k_kirjoita, .k_osoite,
    .x_kelpaa, .x,
    .valmis(valmis_r), .y_kelpaa(kelpaa_r), .y(y_r));
  suodin #(.RINNAKKAIN(1'b0)) j (.clk, .nollaus, .k_kirjoita, .k_osoite,
    .x_kelpaa, .x,
    .valmis(valmis_j), .y_kelpaa(kelpaa_j), .y(y_j));

  initial while (kaynnissa) #5 clk = ~clk;
  always @(posedge clk) jaksot <= jaksot + 1;

  // @alku nayte
  // Tulostaa molempien versioiden tuloksen samalle riville.
  task automatic nayte(input logic [7:0] arvo);
    logic [17:0] tulos_r;
    x = arvo;
    x_kelpaa = 1'b1;
    @(posedge clk); #1 x_kelpaa = 1'b0;
    tulos_r = y_r;
    if (!valmis_r || !kelpaa_r) $fatal(1, "rinnakkainen versio jäljessä");
    while (!kelpaa_j) begin @(posedge clk); #1; end
    $display("x=%3d  rinnakkain y=%5d  jaettu y=%5d", arvo, tulos_r,
                y_j);
    if (tulos_r != y_j) $fatal(1, "versiot eroavat");
    while (!valmis_j) begin @(posedge clk); #1; end
  endtask
  // @loppu nayte

  initial begin
    // Kertoimet 3, 5, 7 ja 9 kirjoitetaan x-väylän kautta.
    for (int i = 0; i < 4; i++) begin
      k_kirjoita = 1'b1;
      k_osoite = 2'(i);
      x = 8'(3 + 2 * i);
      @(posedge clk); #1;
    end
    k_kirjoita = 1'b0;
    nollaus = 1'b0;
    nayte(8'd1);
    repeat (3) nayte(8'd0);
    repeat (4) nayte(8'd10);
    $display("8 näytettä, %0d kellojaksoa", jaksot);
    kaynnissa = 1'b0;
  end
endmodule
