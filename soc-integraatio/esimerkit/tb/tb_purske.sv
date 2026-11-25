// Testipenkki: sama 64 sanan kopio AXI4-väylällä kahdella tavalla,
// sana kerrallaan (kuten AXI4-Lite) ja 16 sanan INCR-purskeina.
// Lopuksi kaksi tahallista protokollavirhettä, jotka tarkistimen on
// huomattava.
module tb_purske;
  localparam int SANAT = 64;
  localparam logic [31:0] LAHDE = 32'h0000_0000, KOHDE = 32'h0000_0400;

  logic        kello = 1'b0, nollaus_n = 1'b0;
  logic [31:0] araddr = '0, awaddr = '0, wdata = '0, rdata;
  logic [7:0]  arlen = '0, awlen = '0;
  logic        arvalid = 1'b0, arready, rlast, rvalid, rready = 1'b0;
  logic        awvalid = 1'b0, awready, wlast = 1'b0, wvalid = 1'b0, wready;
  logic        bvalid, bready = 1'b0;
  int          jakso = 0;

  ram_purske u_ram (.*);
  axi_purske_tarkistin u_tark (.*);

  initial forever #5 kello = ~kello;
  always @(posedge kello) jakso <= jakso + 1;

`ifdef JALJITYS
  // Aaltomuoto kirjan ajoituskaaviota varten (Makefilen kaaviokohde).
  initial begin
    $dumpfile("build/purske.vcd");
    $dumpvars(1, tb_purske);
  end
`endif

  // @alku isanta
  // Isäntä ajaa signaalit kellon laskevalla reunalla ja lukee orjan
  // vastaukset samalla reunalla, jolloin ne ovat vakaat. Kättely
  // tapahtuu seuraavalla nousevalla reunalla.
  //
  // Lukupurske: yksi osoite, n datasiirtoa. Isäntä pitää RREADYn
  // ylhäällä, joten orja voi antaa sanan joka jaksolla.
  task automatic lue(input logic [31:0] osoite, input int n,
                     output logic [31:0] data [16]);
    int i = 0;
    araddr = osoite; arlen = 8'(n - 1); arvalid = 1'b1;
    while (!arready) @(negedge kello);
    @(negedge kello);
    arvalid = 1'b0; rready = 1'b1;
    while (i < n) begin
      if (rvalid) begin
        data[i] = rdata;
        i = i + 1;
      end
      @(negedge kello);
    end
    rready = 1'b0;
  endtask

  // Kirjoituspurske: osoite, n datasiirtoa ja yksi vastaus. WLAST
  // nousee siirrossa `viimeinen` (oletus: oikeassa eli viimeisessä).
  task automatic kirjoita(input logic [31:0] osoite, input int n,
                          input logic [31:0] data [16],
                          input int viimeinen = -1);
    awaddr = osoite; awlen = 8'(n - 1); awvalid = 1'b1;
    while (!awready) @(negedge kello);
    @(negedge kello);
    awvalid = 1'b0;
    for (int i = 0; i < n; i++) begin
      wdata = data[i]; wvalid = 1'b1;
      wlast = (i == (viimeinen < 0 ? n - 1 : viimeinen));
      while (!wready) @(negedge kello);
      @(negedge kello);
    end
    wvalid = 1'b0; wlast = 1'b0; bready = 1'b1;
    while (!bvalid) @(negedge kello);
    @(negedge kello);
    bready = 1'b0;
  endtask
  // @loppu isanta

  // Kopioi SANAT sanaa purskeen pituudella n ja palauttaa kellojaksot.
  task automatic kopioi(input int n, output int kesto);
    logic [31:0] puskuri [16];
    int alku;
    alku = jakso;
    for (int s = 0; s < SANAT; s += n) begin
      lue(LAHDE + 32'(4 * s), n, puskuri);
      kirjoita(KOHDE + 32'(4 * s), n, puskuri);
    end
    kesto = jakso - alku;
  endtask

  function automatic int virheet();
    int v = 0;
    for (int i = 0; i < SANAT; i++)
      if (u_ram.muisti[256 + i] !== u_ram.muisti[i]) v++;
    return v;
  endfunction

  initial begin
    int kesto;
    logic [31:0] puskuri [16];
    for (int i = 0; i < SANAT; i++)
      u_ram.muisti[i] = 32'd100 + 32'(i);
    repeat (3) @(negedge kello);
    nollaus_n = 1'b1;
    @(negedge kello);

    // Ajoituskaavion purske: neljä sanaa luetaan ja kirjoitetaan.
    lue(LAHDE, 4, puskuri);
    kirjoita(KOHDE, 4, puskuri);
    repeat (2) @(negedge kello);

    kopioi(1, kesto);
    $display("sana kerrallaan: %0d sanaa, %0d jaksoa, väärin %0d",
             SANAT, kesto, virheet());
    for (int i = 0; i < SANAT; i++) u_ram.muisti[256 + i] = '0;
    kopioi(16, kesto);
    $display("16 sanan purskeet: %0d sanaa, %0d jaksoa, väärin %0d",
             SANAT, kesto, virheet());
    $display("rikkomuksia oikeissa siirroissa: %0d", u_tark.rikkomuksia);

    // Tahalliset virheet: purske sivun rajan yli ja WLAST liian aikaisin.
    lue(32'h0000_0FF8, 4, puskuri);
    kirjoita(32'h0000_0800, 4, puskuri, 1);
    @(negedge kello);
    $display("rikkomuksia yhteensä: %0d", u_tark.rikkomuksia);
    $finish;
  end
endmodule
