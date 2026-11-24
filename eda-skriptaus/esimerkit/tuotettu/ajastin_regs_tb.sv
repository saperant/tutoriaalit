// Tuotettu tiedostosta asetukset/rekisterit.toml (vuo/rekisterit.py).
// Älä muokkaa käsin: muutokset tehdään kuvaukseen.
module ajastin_regs_tb;
  logic clk = 1'b0, rst_n = 1'b0, kirjoita = 1'b0;
  logic [7:0] osoite = '0;
  logic [31:0] wdata = '0, rdata;
  logic        ctrl_en;
  logic        ctrl_ie;
  logic [7:0]  ctrl_jakaja;
  logic        status_valmis;
  logic        status_valmis_aseta = 1'b0;
  logic [15:0] laskuri_arvo = 16'h5555;
  logic [15:0] vertaa_arvo;
  int virheet = 0, tarkistuksia = 0;

  ajastin_regs dut (.*);
  initial forever #5 clk = ~clk;

  task automatic tarkista(input logic ehto, input string mita);
    tarkistuksia++;
    if (!ehto) begin
      virheet++;
      $display("VIRHE %s", mita);
    end
  endtask

  task automatic lue(input logic [7:0] o, input logic [31:0] arvo,
                     input logic [31:0] maski, input string mita);
    @(negedge clk) osoite = o;
    #1 tarkista((rdata & maski) == arvo, mita);
  endtask

  task automatic kirjoita_rek(input logic [7:0] o,
                              input logic [31:0] d);
    @(negedge clk) begin
      osoite = o; wdata = d; kirjoita = 1'b1;
    end
    @(negedge clk) kirjoita = 1'b0;
  endtask

  initial begin
    #12 rst_n = 1'b1;
    tarkista(ctrl_en == 1'h0, "CTRL.EN lähtö nollauksessa");
    tarkista(ctrl_ie == 1'h0, "CTRL.IE lähtö nollauksessa");
    tarkista(ctrl_jakaja == 8'h1, "CTRL.JAKAJA lähtö nollauksessa");
    lue(8'h00, 32'h00000100, 32'h0000FF03, "CTRL nollausarvo");
    tarkista(status_valmis == 1'h0, "STATUS.VALMIS lähtö nollauksessa");
    lue(8'h04, 32'h00000000, 32'h00000001, "STATUS nollausarvo");
    lue(8'h08, 32'h00005555, 32'h0000FFFF, "LASKURI nollausarvo");
    tarkista(vertaa_arvo == 16'hFFFF, "VERTAA.ARVO lähtö nollauksessa");
    lue(8'h0C, 32'h0000FFFF, 32'h0000FFFF, "VERTAA nollausarvo");
    kirjoita_rek(8'h00, 32'hFFFFFFFF);
    lue(8'h00, 32'h0000FF03, 32'h0000FF03, "CTRL kirjoitus");
    kirjoita_rek(8'h04, 32'hFFFFFFFF);
    lue(8'h04, 32'h00000000, 32'h00000001, "STATUS kirjoitus");
    kirjoita_rek(8'h08, 32'hFFFFFFFF);
    lue(8'h08, 32'h00005555, 32'h0000FFFF, "LASKURI kirjoitus");
    kirjoita_rek(8'h0C, 32'hFFFFFFFF);
    lue(8'h0C, 32'h0000FFFF, 32'h0000FFFF, "VERTAA kirjoitus");
    @(negedge clk) status_valmis_aseta = 1'b1;
    @(negedge clk) status_valmis_aseta = 1'b0;
    lue(8'h04, 32'h00000001, 32'h00000001, "STATUS.VALMIS asetettu");
    kirjoita_rek(8'h04, 32'h00000001);
    lue(8'h04, 32'h0, 32'h00000001, "STATUS.VALMIS nollattu");
    if (virheet == 0)
      $display("REKISTERITESTI OK %0d tarkistusta", tarkistuksia);
    else $display("REKISTERITESTI EPÄONNISTUI %0d virhettä", virheet);
    $finish;
  end
endmodule
