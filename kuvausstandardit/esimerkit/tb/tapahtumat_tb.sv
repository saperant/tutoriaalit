// Kenttien kayttaytymisen testipenkki: kertapulssi, kirjoitus- ja
// lukuilmoitukset, saturoituva laskuri, lukemalla nollautuva kentta
// ja keskeytysliput sallintoineen.

module tapahtumat_tb;
    logic clk = 0, rst = 1;
    initial forever #5 clk = ~clk;

    logic psel = 0, penable = 0, pwrite = 0;
    logic [4:0] paddr = 0;
    logic [31:0] pwdata = 0, prdata;
    logic pready, pslverr;
    int virheet = 0;
    logic vaylavirhe = 0;

    tapahtumat_pkg::tapahtumat__in_t hwif_in;
    tapahtumat_pkg::tapahtumat__out_t hwif_out;

    tapahtumat dut (
        .clk, .rst,
        .s_apb_psel(psel), .s_apb_penable(penable),
        .s_apb_pwrite(pwrite), .s_apb_pprot(3'b000),
        .s_apb_paddr(paddr), .s_apb_pwdata(pwdata),
        .s_apb_pstrb(4'hF), .s_apb_pready(pready),
        .s_apb_prdata(prdata), .s_apb_pslverr(pslverr),
        .hwif_in, .hwif_out);

    `include "apb.svh"

    // @alku havainnot
    // Laitteiston puolen havainnot: montako jaksoa pulssi kesti ja
    // montako kirjoitus- ja lukuilmoitusta tuli.
    int pulssi = 0, kirjoitukset = 0, luvut = 0;
    always @(negedge clk) begin
        if (hwif_out.OHJAUS.KAYNNISTA.value) pulssi <= pulssi + 1;
        if (hwif_out.OHJAUS.TILA.swmod) kirjoitukset <= kirjoitukset + 1;
        if (hwif_out.NAYTE.ARVO.swacc) luvut <= luvut + 1;
    end
    // @loppu havainnot

    // incr on ylhaalla n nousevan reunan ajan.
    task automatic tapahtumia(input int n);
        @(negedge clk) hwif_in.TAPAHTUMAT.MAARA.incr = 1;
        repeat (n) @(negedge clk);
        hwif_in.TAPAHTUMAT.MAARA.incr = 0;
    endtask

    initial begin
        hwif_in.TAPAHTUMAT.MAARA.incr = 0;
        hwif_in.KESKEYTYS.YLIVUOTO.hwset = 0;
        hwif_in.KESKEYTYS.VIRHE.hwset = 0;
        hwif_in.NAYTE.ARVO.next = 32'hCAFE_0042;
        repeat (3) @(negedge clk);
        rst = 0;

        // @alku testit
        kirjoita('h00, 32'h0000_0001);
        odota('h00, 32'h0000_0000, "KAYNNISTA lukee aina 0");
        huomio($sformatf("KAYNNISTA-pulssi: %0d jakso", pulssi));
        kirjoita('h00, 32'h0000_0030);
        odota('h00, 32'h0000_0030, "TILA kirjoitettu");
        huomio($sformatf("TILA swmod: %0d kertaa", kirjoitukset));

        tapahtumia(5);
        odota('h04, 32'h0000_0005, "TAPAHTUMAT laski 5");
        odota('h04, 32'h0000_0000, "TAPAHTUMAT nollautui luettaessa");
        tapahtumia(70000);
        odota('h04, 32'h0000_FFFF, "TAPAHTUMAT saturoitui");

        @(negedge clk) hwif_in.KESKEYTYS.VIRHE.hwset = 1;
        @(negedge clk) hwif_in.KESKEYTYS.VIRHE.hwset = 0;
        odota('h08, 32'h0000_0002, "KESKEYTYS.VIRHE asettui");
        huomio($sformatf("keskeytys ennen sallintaa: %0d",
                         hwif_out.KESKEYTYS.intr));
        kirjoita('h0C, 32'h0000_0002);
        huomio($sformatf("keskeytys sallittuna: %0d",
                         hwif_out.KESKEYTYS.intr));
        kirjoita('h08, 32'h0000_0002);
        odota('h08, 32'h0000_0000, "KESKEYTYS kuitattu");
        huomio($sformatf("keskeytys kuittauksen jalkeen: %0d",
                         hwif_out.KESKEYTYS.intr));

        odota('h10, 32'hCAFE_0042, "NAYTE luettu");
        huomio($sformatf("NAYTE swacc: %0d kertaa", luvut));
        // @loppu testit

        $display("REKISTERITESTI: %0d virhetta", virheet);
        $finish;
    end
endmodule
