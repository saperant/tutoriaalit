// Sekvenssin 101 tunnistin Moore- ja Mealy-tilakoneena.

// @alku moore
module tunnistin_moore (
  input  logic clk,
  input  logic nollaa,
  input  logic x,
  output logic z
);
  typedef enum logic [1:0] {S0, S1, S2, S3} tila_t;  // S3 = nähty 101
  tila_t tila, seuraava;

  always_ff @(posedge clk) begin
    if (nollaa) tila <= S0;
    else        tila <= seuraava;
  end

  always_comb begin
    unique case (tila)
      S0: seuraava = x ? S1 : S0;
      S1: seuraava = x ? S1 : S2;
      S2: seuraava = x ? S3 : S0;
      S3: seuraava = x ? S1 : S2;
    endcase
  end

  assign z = (tila == S3);       // Moore: lähtö vain tilasta
endmodule
// @loppu moore

// @alku mealy
module tunnistin_mealy (
  input  logic clk,
  input  logic nollaa,
  input  logic x,
  output logic z
);
  typedef enum logic [1:0] {A, B, C} tila_t;         // C = nähty 10
  tila_t tila, seuraava;

  always_ff @(posedge clk) begin
    if (nollaa) tila <= A;
    else        tila <= seuraava;
  end

  always_comb begin
    seuraava = A;
    unique case (tila)
      A: seuraava = x ? B : A;
      B: seuraava = x ? B : C;
      C: seuraava = x ? B : A;
      default: seuraava = A;
    endcase
  end

  assign z = (tila == C) && x;   // Mealy: lähtö tilasta ja syötteestä
endmodule
// @loppu mealy

// @alku testipenkki
module testipenkki;
  logic clk = 1'b0, kaynnissa = 1'b1, nollaa = 1'b1, x = 1'b0;
  logic z_moore, z_mealy;
  logic [9:0] syote = 10'b1011010100;
  string rivi_x = "", rivi_mealy = "", rivi_moore = "";

  tunnistin_moore u_moore (.clk, .nollaa, .x, .z(z_moore));
  tunnistin_mealy u_mealy (.clk, .nollaa, .x, .z(z_mealy));

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    @(posedge clk); #1 nollaa = 1'b0;
    for (int j = 9; j >= 0; j--) begin
      x = syote[j];                 // syöte asettuu reunan jälkeen
      #3;                           // näytteet ennen seuraavaa reunaa
      rivi_x     = {rivi_x,     $sformatf("%b ", x)};
      rivi_mealy = {rivi_mealy, $sformatf("%b ", z_mealy)};
      rivi_moore = {rivi_moore, $sformatf("%b ", z_moore)};
      @(posedge clk); #1;
    end
    $display("syöte  %s", rivi_x);
    $display("Mealy  %s", rivi_mealy);
    $display("Moore  %s", rivi_moore);
    kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
