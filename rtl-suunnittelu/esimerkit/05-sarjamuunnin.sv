// @alku siirtorekisteri
// Sarjasta rinnakkaiseksi: vastaanottaa bitit vähiten merkitsevä
// ensin ja ilmoittaa valmis-pulssilla, kun tavu on koossa.
module sarjasta_rinnakkais (
  input  logic       clk,
  input  logic       rst_n,
  input  logic       bitti_kelvollinen,
  input  logic       bitti,
  output logic [7:0] tavu,
  output logic       valmis              // yhden jakson pulssi
);
  logic [2:0] laskuri;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      tavu    <= '0;
      laskuri <= '0;
      valmis  <= 1'b0;
    end else begin
      valmis <= 1'b0;                    // oletus: ei pulssia
      if (bitti_kelvollinen) begin
        tavu    <= {bitti, tavu[7:1]};   // uusi bitti ylös, siirto alas
        laskuri <= laskuri + 1'b1;
        valmis  <= (laskuri == 3'd7);
      end
    end
  end
endmodule
// @loppu siirtorekisteri

// @alku reuna
// Nousevan reunan tunnistin: pulssi, kun signaali vaihtuu 0 -> 1.
module nouseva_reuna (
  input  logic clk,
  input  logic rst_n,
  input  logic signaali,
  output logic pulssi
);
  logic edellinen;
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) edellinen <= 1'b0;
    else        edellinen <= signaali;
  end
  assign pulssi = signaali & ~edellinen;
endmodule
// @loppu reuna

module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1, rst_n = 1'b0;
  logic       kelvollinen = 1'b0, bitti = 1'b0;
  logic [7:0] tavu;
  logic       valmis, pulssi;
  int         pulsseja = 0;

  sarjasta_rinnakkais u_sr (.clk, .rst_n, .bitti_kelvollinen(kelvollinen),
                            .bitti, .tavu, .valmis);
  nouseva_reuna u_reuna (.clk, .rst_n, .signaali(bitti), .pulssi);

  initial while (kaynnissa) #5 clk = ~clk;
  always @(posedge clk) if (pulssi) pulsseja <= pulsseja + 1;

  task automatic laheta(logic [7:0] arvo);
    for (int i = 0; i < 8; i++) begin
      kelvollinen = 1'b1;
      bitti       = arvo[i];
      @(posedge clk); #1;
    end
    kelvollinen = 1'b0;
    bitti       = 1'b0;
  endtask

  initial begin
    #12 rst_n = 1'b1;
    @(posedge clk); #1;
    laheta(8'hA5);
    $display("vastaanotettu %h, valmis = %b", tavu, valmis);
    laheta(8'h3C);
    $display("vastaanotettu %h, valmis = %b", tavu, valmis);
    @(posedge clk); #1;
    $display("valmis-pulssi kesti yhden jakson: valmis = %b", valmis);
    $display("nousevia reunoja bittivirrassa: %0d", pulsseja);
    if (tavu != 8'h3C || pulsseja != 5) $fatal(1, "väärä tulos");
    kaynnissa = 1'b0;
  end
endmodule
