// @alku kartta
// Ohjausrekisteripankki, jota prosessori käyttää väylän kautta.
//   0x0 OHJAUS     RW  [0] käynnissä, [15:8] jakaja
//   0x4 TILA       RO  [0] käynnissä, [1] keskeytys odottaa
//   0x8 KESKEYTYS  W1C [0] ajastin laukesi (1 kuittaa, 0 ei vaikuta)
//   0xC LASKURI    RO  laukeamisten määrä
module rekisteripankki (
  input  logic        clk,
  input  logic        rst_n,
  // Väylä: kirjoitus tai luku yhdellä jaksolla, lukudata seuraavalla.
  input  logic        valinta,
  input  logic        kirjoitus,
  input  logic [3:0]  osoite,
  // Väylä on 32-bittinen, mutta kaikkia bittejä ei käytetä.
  /* verilator lint_off UNUSEDSIGNAL */
  input  logic [31:0] k_data,
  /* verilator lint_on UNUSEDSIGNAL */
  output logic [31:0] l_data,
  // Laitteiston puoli
  output logic        kaynnissa,
  output logic [7:0]  jakaja,
  input  logic        laukesi,        // yhden jakson pulssi
  output logic        keskeytys
);
  localparam logic [3:0] OHJAUS = 4'h0, TILA = 4'h4,
                         KESKEYTYS = 4'h8, LASKURI = 4'hC;
  // @loppu kartta

  // @alku rekisterit
  logic        odottaa;
  logic [31:0] laskuri;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      kaynnissa <= 1'b0;
      jakaja    <= 8'd1;
      odottaa   <= 1'b0;
      laskuri   <= '0;
      l_data    <= '0;
    end else begin
      if (valinta && kirjoitus && osoite == OHJAUS) begin
        kaynnissa <= k_data[0];
        jakaja    <= k_data[15:8];
      end
      // W1C: laitteiston asetus voittaa samanaikaisen kuittauksen,
      // jotta yhtään tapahtumaa ei menetetä.
      if (laukesi)
        odottaa <= 1'b1;
      else if (valinta && kirjoitus && osoite == KESKEYTYS && k_data[0])
        odottaa <= 1'b0;
      if (laukesi) laskuri <= laskuri + 1;

      if (valinta && !kirjoitus) begin
        unique case (osoite)
          OHJAUS:    l_data <= {16'b0, jakaja, 7'b0, kaynnissa};
          TILA:      l_data <= {30'b0, odottaa, kaynnissa};
          KESKEYTYS: l_data <= {31'b0, odottaa};
          LASKURI:   l_data <= laskuri;
          default:   l_data <= 32'hDEAD_BEEF;   // tunnistettava arvo
        endcase
      end
    end
  end

  assign keskeytys = odottaa;
  // @loppu rekisterit
endmodule

module testipenkki;
  logic        clk = 1'b0, kaynnissa_tb = 1'b1, rst_n = 1'b0;
  logic        valinta = 1'b0, kirjoitus = 1'b0, laukesi = 1'b0;
  logic [3:0]  osoite = '0;
  logic [31:0] k_data = '0, l_data, luettu;
  logic        kaynnissa, keskeytys;
  logic [7:0]  jakaja;

  rekisteripankki u_rp (.clk, .rst_n, .valinta, .kirjoitus, .osoite,
                        .k_data, .l_data, .kaynnissa, .jakaja, .laukesi,
                        .keskeytys);

  initial while (kaynnissa_tb) #5 clk = ~clk;

  // @alku vayla
  task automatic kirjoita(logic [3:0] os, logic [31:0] arvo);
    {valinta, kirjoitus, osoite, k_data} = {1'b1, 1'b1, os, arvo};
    @(posedge clk); #1;
    {valinta, kirjoitus} = '0;
  endtask

  task automatic lue(logic [3:0] os, output logic [31:0] arvo);
    {valinta, kirjoitus, osoite} = {1'b1, 1'b0, os};
    @(posedge clk); #1;
    valinta = 1'b0;
    arvo    = l_data;
  endtask
  // @loppu vayla

  initial begin
    #12 rst_n = 1'b1;
    kirjoita(4'h0, 32'h0000_2A01);
    lue(4'h0, luettu);
    $display("OHJAUS = %h, käynnissä = %b, jakaja = %0d", luettu,
             kaynnissa, jakaja);
    laukesi = 1'b1; @(posedge clk); #1; laukesi = 1'b0;
    lue(4'h4, luettu);
    $display("TILA = %h, keskeytys = %b", luettu, keskeytys);
    kirjoita(4'h8, 32'h0);                // 0 ei kuittaa
    $display("0 kirjoitettu: keskeytys = %b", keskeytys);
    // Kuittaus ja uusi laukeaminen samalla jaksolla.
    laukesi = 1'b1;
    kirjoita(4'h8, 32'h1);
    laukesi = 1'b0;
    $display("kuittaus + laukeaminen: keskeytys = %b", keskeytys);
    kirjoita(4'h8, 32'h1);
    $display("kuittaus: keskeytys = %b", keskeytys);
    lue(4'hC, luettu);
    $display("LASKURI = %0d", luettu);
    lue(4'h6, luettu);
    $display("tuntematon osoite 0x6: %h", luettu);
    if (keskeytys || luettu != 32'hDEAD_BEEF) $fatal(1, "pankki väärin");
    kaynnissa_tb = 1'b0;
  end
endmodule
