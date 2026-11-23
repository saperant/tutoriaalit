// @alku tahti
// Tahtigeneraattori: yhden jakson pulssi joka JAKAJA:nnella jaksolla.
// Pulssia käytetään kellon sallintana (clock enable), ei kellona.
module tahti #(parameter int JAKAJA = 50) (
  input  logic clk,
  input  logic rst_n,
  output logic tick
);
  localparam int LW = $clog2(JAKAJA);
  logic [LW-1:0] laskuri;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      laskuri <= '0;
      tick    <= 1'b0;
    end else begin
      tick    <= (laskuri == LW'(JAKAJA - 1));
      laskuri <= (laskuri == LW'(JAKAJA - 1)) ? '0 : laskuri + 1'b1;
    end
  end
endmodule
// @loppu tahti

// @alku pwm
// PWM: jakso 2**W tickiä. Uusi pulssisuhde otetaan käyttöön vasta
// jakson alussa (varjorekisteri), jotta yksikään pulssi ei katkea.
module pwm #(parameter int W = 8) (
  input  logic         clk,
  input  logic         rst_n,
  input  logic         tick,          // etenee vain tickillä
  input  logic [W-1:0] suhde,         // 0 = aina 0, 2**W-1 lähes aina 1
  output logic         ulos
);
  logic [W-1:0] vaihe, voimassa;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      vaihe    <= '0;
      voimassa <= '0;
      ulos     <= 1'b0;
    end else if (tick) begin
      vaihe <= vaihe + 1'b1;
      if (vaihe == '1) voimassa <= suhde;   // seuraava jakso alkaa
      ulos <= (vaihe < voimassa);
    end
  end
endmodule
// @loppu pwm

module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic       tick, ulos;
  logic [3:0] suhde = 4'd4;
  int         ykkosia;
  int         pyynnot[4] = '{4, 12, 0, 15};

  tahti #(.JAKAJA(3)) u_tahti (.clk, .rst_n, .tick);
  pwm   #(.W(4))      u_pwm   (.clk, .rst_n, .tick, .suhde, .ulos);

  initial while (kaynnissa) #5 clk = ~clk;

  // Mittaa yhden PWM-jakson (16 tickiä) ykkösten määrän.
  task automatic mittaa(output int n);
    n = 0;
    for (int i = 0; i < 16; i++) begin
      @(posedge clk iff tick); #1;
      n += int'(ulos);
    end
  endtask

  initial begin
    #12 rst_n = 1'b1;
    mittaa(ykkosia);                      // käynnistysjakso: suhde 0
    foreach (pyynnot[k]) begin
      int pyydetty = pyynnot[k];
      suhde = 4'(pyydetty);
      mittaa(ykkosia);                    // tämä jakso: vanha suhde
      mittaa(ykkosia);                    // uusi suhde voimassa
      $display("suhde %2d/16: ulostulo 1 %2d tickiä jaksosta",
               pyydetty, ykkosia);
      if (ykkosia != pyydetty) $fatal(1, "väärä pulssisuhde");
    end
    kaynnissa = 1'b0;
  end
endmodule
