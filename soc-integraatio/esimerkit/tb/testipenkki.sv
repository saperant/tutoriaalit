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

  always @(posedge kello)
    if (lopeta) begin
      if (paluukoodi != 8'd0)
        $fatal(1, "ohjelma päättyi koodilla %0d", paluukoodi);
      $finish;
    end

endmodule
