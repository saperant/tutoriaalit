// Testipenkki: SoC, ohjelman lataus, UART-vastaanotin ja GPIO-silmukka.
//
//   +ohjelma=TIEDOSTO   ladattava ohjelma ($readmemh-muoto)
//   +jaksot=N           enimmäiskesto kellojaksoina (oletus 2 000 000)
//
// Ohjelma päättää simulaation kirjoittamalla paluukoodin SYSCONin
// LOPETA-rekisteriin; muu kuin nolla on virhe.
module testipenkki;

  logic       kello = 1'b0;
  logic       nollaus_n = 1'b0;
  logic       uart_tx, lopeta;
  logic [7:0] gpio_ulos, paluukoodi;

  // GPIO:n lähdöt kytketään takaisin tuloihin, joten ohjelma voi
  // aiheuttaa itselleen keskeytyksen.
  soc u_soc (.kello, .nollaus_n, .uart_tx, .gpio_ulos,
             .gpio_sisaan(gpio_ulos), .lopeta, .paluukoodi);

  initial forever #5 kello = ~kello;

  initial begin
    string tiedosto;
    int jaksot = 2_000_000;
    if (!$value$plusargs("ohjelma=%s", tiedosto))
      $fatal(1, "anna +ohjelma=TIEDOSTO");
    void'($value$plusargs("jaksot=%d", jaksot));
    $readmemh(tiedosto, u_soc.u_ram.muisti);
    repeat (3) @(posedge kello);
    nollaus_n = 1'b1;
    repeat (jaksot) @(posedge kello);
    $fatal(1, "aikakatkaisu: ohjelma ei päättynyt");
  end

  // @alku vastaanotin
  // UART-vastaanotin: odottaa aloitusbitin, näytteistää bittien keskeltä
  // ja tulostaa merkin. Bittiaika luetaan UARTin JAKAJA-rekisteristä.
  initial begin
    logic [7:0] merkki;
    forever begin
      @(negedge uart_tx);
      repeat (int'(u_soc.u_uart.jakaja) * 3 / 2) @(posedge kello);
      for (int i = 0; i < 8; i++) begin
        merkki[i] = uart_tx;
        repeat (int'(u_soc.u_uart.jakaja)) @(posedge kello);
      end
      $write("%c", merkki);
    end
  end
  // @loppu vastaanotin

`ifdef JALJITYS
  // Kirjan ajoituskaaviot (make kaaviot): APB-sillalle tuleva AXI4-Lite-
  // väylä ja sillalta UARTille lähtevä APB. Rakenteiden kentät tuodaan
  // omiksi johdoikseen, jotta aaltomuodossa ne ovat erillisiä signaaleja.
  /* verilator lint_off UNUSEDSIGNAL */
  wire        awvalid = u_soc.orja_m[1].awvalid;
  wire        awready = u_soc.orja_s[1].awready;
  wire [31:0] awaddr  = u_soc.orja_m[1].awaddr;
  wire        wvalid  = u_soc.orja_m[1].wvalid;
  wire        wready  = u_soc.orja_s[1].wready;
  wire [31:0] wdata   = u_soc.orja_m[1].wdata;
  wire        bvalid  = u_soc.orja_s[1].bvalid;
  wire        bready  = u_soc.orja_m[1].bready;
  wire        psel    = u_soc.apb_m[0].psel;
  wire        penable = u_soc.apb_m[0].penable;
  wire        pwrite  = u_soc.apb_m[0].pwrite;
  wire [11:0] paddr   = u_soc.apb_m[0].paddr;
  wire [31:0] pwdata  = u_soc.apb_m[0].pwdata;
  wire        pready  = u_soc.apb_s[0].pready;
  // Keskeytyksen kulku (luku 9): GPIO:n tulosta ytimen ansaan.
  wire        g_tulo   = gpio_ulos[0];
  wire        g_reunat = u_soc.u_gpio.reunat[0];
  wire        g_kesk   = u_soc.gpio_kesk;
  wire        meip     = u_soc.ulkoinen_kesk;
  wire [1:0]  y_tila   = u_soc.u_ydin.tila;
  wire [31:0] y_pc     = u_soc.u_ydin.pc;
  wire [31:0] y_mcause = u_soc.u_ydin.mcause;
  // DMA:n ja ytimen siirrot kytkimen isäntäporteissa (luku 10).
  wire        y_arvalid = u_soc.isanta_m[0].arvalid;
  wire        y_rvalid  = u_soc.isanta_s[0].rvalid;
  wire        d_arvalid = u_soc.isanta_m[1].arvalid;
  wire        d_arready = u_soc.isanta_s[1].arready;
  wire        d_rvalid  = u_soc.isanta_s[1].rvalid;
  wire        d_awvalid = u_soc.isanta_m[1].awvalid;
  wire        d_wvalid  = u_soc.isanta_m[1].wvalid;
  wire        d_bvalid  = u_soc.isanta_s[1].bvalid;
  wire [2:0]  d_tila    = u_soc.u_dma.tila;
  /* verilator lint_on UNUSEDSIGNAL */
  initial begin
    $dumpfile("build/jalki.vcd");
    $dumpvars(1, testipenkki);
  end
`endif

  always @(posedge kello)
    if (lopeta) begin
      if (paluukoodi != 8'd0)
        $fatal(1, "ohjelma päättyi koodilla %0d", paluukoodi);
      $finish;
    end

endmodule
