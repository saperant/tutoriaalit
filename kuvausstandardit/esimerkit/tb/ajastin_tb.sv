// PeakRDL-regblockin tuottaman ajastinlohkon testipenkki. Lohko
// kytketaan APB4-vaylaan, ja laitteiston puoli (hwif_in, hwif_out)
// ohjataan suoraan.

module ajastin_tb;
    logic clk = 0, rst = 1;
    initial forever #5 clk = ~clk;

    logic psel = 0, penable = 0, pwrite = 0;
    logic [3:0] paddr = 0;
    logic [31:0] pwdata = 0, prdata;
    logic pready, pslverr;
    int virheet = 0;
    logic vaylavirhe = 0;

    // @alku kytkenta
    ajastin_pkg::ajastin__in_t hwif_in;
    ajastin_pkg::ajastin__out_t hwif_out;

    // Laitteiston tulot ajetaan omista muuttujista jatkuvilla
    // sijoituksilla, jolloin lohkon kombinaatiologiikka nakee muutoksen
    // heti eika vasta seuraavalla kellon reunalla.
    logic        valmis_hwset = 0;
    logic [15:0] laskuri = 16'h1234;
    assign hwif_in.STATUS.VALMIS.hwset = valmis_hwset;
    assign hwif_in.LASKURI.ARVO.next   = laskuri;

    ajastin dut (
        .clk, .rst,
        .s_apb_psel(psel), .s_apb_penable(penable),
        .s_apb_pwrite(pwrite), .s_apb_pprot(3'b000),
        .s_apb_paddr(paddr), .s_apb_pwdata(pwdata),
        .s_apb_pstrb(4'hF), .s_apb_pready(pready),
        .s_apb_prdata(prdata), .s_apb_pslverr(pslverr),
        .hwif_in, .hwif_out);
    // @loppu kytkenta

    `include "apb.svh"

    initial begin
        repeat (3) @(negedge clk);
        rst = 0;

        // @alku testit
        odota('h0, 32'h0000_0100, "CTRL nollausarvo (JAKAJA=1)");
        odota('hC, 32'h0000_FFFF, "VERTAA nollausarvo");
        kirjoita('h0, 32'hFFFF_0503);
        odota('h0, 32'h0000_0503, "CTRL: kuvaamattomat bitit 0");
        raportoi(hwif_out.CTRL.JAKAJA.value == 8'h05
                 && hwif_out.CTRL.EN.value == 1,
                 "          CTRL nakyy laitteistolle");
        odota('h8, 32'h0000_1234, "LASKURI: laitteiston arvo");
        kielletty('h8, "LASKURI: kirjoitus kielletty");
        odota('h8, 32'h0000_1234, "LASKURI ennallaan");

        @(negedge clk) valmis_hwset = 1;
        @(negedge clk) valmis_hwset = 0;
        odota('h4, 32'h0000_0001, "STATUS.VALMIS asettui");
        huomio($sformatf("keskeytys, IE=1: %0d", hwif_out.STATUS.intr));
        kirjoita('h0, 32'h0000_0501);
        huomio($sformatf("keskeytys, IE=0: %0d", hwif_out.STATUS.intr));
        kirjoita('h4, 32'h0000_0000);
        odota('h4, 32'h0000_0001, "STATUS: 0:n kirjoitus ei nollaa");
        kirjoita('h4, 32'h0000_0001);
        odota('h4, 32'h0000_0000, "STATUS: 1:n kirjoitus nollaa");
        // @loppu testit

        $display("REKISTERITESTI: %0d virhetta", virheet);
        $finish;
    end
endmodule
