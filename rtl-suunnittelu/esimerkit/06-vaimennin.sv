// @alku vaimennin
// Painonapin värähtelyn vaimennin. Raaka sisääntulo tahdistetaan
// ensin kahdella kiikulla (luku 10), sitten tilakone hyväksyy uuden
// tason vasta, kun se on pysynyt samana VAKAA jaksoa.
module vaimennin #(
  parameter int VAKAA = 1000              // esim. 20 us 50 MHz:llä
) (
  input  logic clk,
  input  logic rst_n,
  input  logic nappi_raaka,               // asynkroninen, värähtelee
  output logic painettu,                  // vaimennettu taso
  output logic painallus                  // pulssi painettaessa
);
  localparam int LW = $clog2(VAKAA);

  typedef enum logic [1:0] {YLHAALLA, PAINUU, ALHAALLA, NOUSEE} tila_t;
  tila_t         tila;
  logic [1:0]    tahdistin;
  logic [LW-1:0] laskuri;
  logic          nappi;

  assign nappi    = tahdistin[1];
  assign painettu = (tila == ALHAALLA) || (tila == NOUSEE);

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      tahdistin <= '0;
      tila      <= YLHAALLA;
      laskuri   <= '0;
      painallus <= 1'b0;
    end else begin
      tahdistin <= {tahdistin[0], nappi_raaka};
      painallus <= 1'b0;
      laskuri   <= laskuri + 1'b1;
      unique case (tila)
        YLHAALLA: begin
          laskuri <= '0;
          if (nappi) tila <= PAINUU;
        end
        PAINUU:
          if (!nappi) tila <= YLHAALLA;      // värähdys: alusta
          else if (laskuri == LW'(VAKAA - 1)) begin
            tila      <= ALHAALLA;
            painallus <= 1'b1;
          end
        ALHAALLA: begin
          laskuri <= '0;
          if (!nappi) tila <= NOUSEE;
        end
        NOUSEE:
          if (nappi) tila <= ALHAALLA;
          else if (laskuri == LW'(VAKAA - 1)) tila <= YLHAALLA;
      endcase
    end
  end
endmodule
// @loppu vaimennin

module testipenkki;
  logic clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic nappi = 1'b0, painettu, painallus;
  int   painalluksia = 0, jaksoja_alhaalla = 0;

  vaimennin #(.VAKAA(8)) u_v (.clk, .rst_n, .nappi_raaka(nappi),
                              .painettu, .painallus);

  initial while (kaynnissa) #5 clk = ~clk;
  always @(posedge clk) begin
    if (painallus) painalluksia <= painalluksia + 1;
    if (painettu)  jaksoja_alhaalla <= jaksoja_alhaalla + 1;
  end

  // Värähtelevä painallus: lyhyitä piikkejä, sitten vakaa taso.
  task automatic varahtele(logic loppu);
    int kestot[6] = '{3, 7, 2, 13, 4, 9};
    foreach (kestot[i]) begin
      nappi = ~nappi;
      #(kestot[i]);
    end
    nappi = loppu;
    #400;
  endtask

  initial begin
    #12 rst_n = 1'b1;
    #50;
    varahtele(1'b1);                      // painetaan
    varahtele(1'b0);                      // päästetään
    varahtele(1'b1);
    varahtele(1'b0);
    nappi = 1'b1; #30; nappi = 1'b0;      // liian lyhyt: häiriö
    #200;
    $display("painalluksia: %0d, alhaalla %0d jaksoa", painalluksia,
             jaksoja_alhaalla);
    if (painalluksia != 2) $fatal(1, "väärä painallusmäärä");
    kaynnissa = 1'b0;
  end
endmodule
