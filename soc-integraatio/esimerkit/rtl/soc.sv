// Pikku-SoC: RV32I-ydin, DMA, AXI4-Lite-kytkin, RAM ja APB-oheislaitteet.
//
//   isännät  0 ydin (silta.sv)        1 DMA
//   AXI      0x0000_0000 RAM 16 KiB   0x1000_0000 APB-silta 64 KiB
//   APB      0x1000_0000 UART         0x1000_1000 SYSCON
//            0x1000_2000 GPIO         0x1000_3000 DMA
//            0x1000_4000 CLINT        0x1000_5000 PLIC
//   PLIC     lähde 1 GPIO, lähde 2 DMA
module soc
  import vaylat::*;
(
  input  logic       kello,
  input  logic       nollaus_n,
  output logic       uart_tx,
  output logic [7:0] gpio_ulos,
  input  logic [7:0] gpio_sisaan,
  output logic       lopeta,        // SYSCON.LOPETA kirjoitettiin
  output logic [7:0] paluukoodi
);

  // @alku kytkenta
  axil_m2s_t isanta_m [2];
  axil_s2m_t isanta_s [2];
  axil_m2s_t orja_m   [2];
  axil_s2m_t orja_s   [2];
  apb_m2s_t  apb_m    [6];
  apb_s2m_t  apb_s    [6];

  logic        v_pyynto, v_kirjoita, v_valmis, v_virhe;
  logic [31:0] v_osoite, v_kdata, v_ldata;
  logic [3:0]  v_tavut;
  logic        ajastin_kesk, ulkoinen_kesk, gpio_kesk, dma_kesk;
  /* verilator lint_off UNUSEDSIGNAL */
  logic [31:0] syscon_apu;            // apurekisteri vain ohjelmistolle
  /* verilator lint_on UNUSEDSIGNAL */

  ydin u_ydin (.kello, .nollaus_n, .v_pyynto, .v_kirjoita, .v_osoite,
               .v_kdata, .v_tavut, .v_valmis, .v_ldata, .v_virhe,
               .ajastin_kesk, .ulkoinen_kesk);

  silta u_silta (.kello, .nollaus_n, .v_pyynto, .v_kirjoita, .v_osoite,
                 .v_kdata, .v_tavut, .v_valmis, .v_ldata, .v_virhe,
                 .m(isanta_m[0]), .s(isanta_s[0]));

  kytkin #(
    .ISANNAT(2), .ORJAT(2),
    .KANTA('{32'h0000_0000, 32'h1000_0000}),
    .MASKI('{32'hFFFF_C000, 32'hFFFF_0000})
  ) u_kytkin (.kello, .nollaus_n, .isanta_m, .isanta_s, .orja_m,
              .orja_s);

  ram       u_ram   (.kello, .nollaus_n, .m(orja_m[0]), .s(orja_s[0]));
  apb_silta u_apb   (.kello, .nollaus_n, .m(orja_m[1]), .s(orja_s[1]),
                     .apb_m, .apb_s);
  // @loppu kytkenta

  // @alku oheislaitteet
  uart u_uart (.kello, .nollaus_n, .apb_m(apb_m[0]), .apb_s(apb_s[0]),
               .tx(uart_tx));

  syscon_regs u_syscon (
    .kello, .nollaus_n, .apb_m(apb_m[1]), .apb_s(apb_s[1]),
    .apu_q(syscon_apu), .lopeta_q(paluukoodi), .lopeta_we(lopeta));

  gpio u_gpio (.kello, .nollaus_n, .apb_m(apb_m[2]), .apb_s(apb_s[2]),
               .ulos(gpio_ulos), .sisaan(gpio_sisaan),
               .keskeytys(gpio_kesk));

  dma u_dma (.kello, .nollaus_n, .apb_m(apb_m[3]), .apb_s(apb_s[3]),
             .m(isanta_m[1]), .s(isanta_s[1]), .keskeytys(dma_kesk));

  clint u_clint (.kello, .nollaus_n, .apb_m(apb_m[4]),
                 .apb_s(apb_s[4]), .ajastin_kesk);

  plic #(.LAHTEET(2)) u_plic (
    .kello, .nollaus_n, .apb_m(apb_m[5]), .apb_s(apb_s[5]),
    .lahteet({dma_kesk, gpio_kesk}), .ulkoinen_kesk);
  // @loppu oheislaitteet

`ifndef SYNTHESIS
  // @alku tarkistimet
  // Protokollatarkistimet jokaiseen AXI-liitäntään (vain simulaatio).
  axil_tarkistin #(.NIMI("ydin"))  t_ydin  (.kello, .nollaus_n,
    .m(isanta_m[0]), .s(isanta_s[0]));
  axil_tarkistin #(.NIMI("dma"))   t_dma   (.kello, .nollaus_n,
    .m(isanta_m[1]), .s(isanta_s[1]));
  axil_tarkistin #(.NIMI("ram"))   t_ram   (.kello, .nollaus_n,
    .m(orja_m[0]), .s(orja_s[0]));
  axil_tarkistin #(.NIMI("apb"))   t_apb   (.kello, .nollaus_n,
    .m(orja_m[1]), .s(orja_s[1]));
  // @loppu tarkistimet
`endif

endmodule
