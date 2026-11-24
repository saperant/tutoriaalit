// Ohjattu testi: täytetään FIFO, tyhjennetään se ja tarkistetaan,
// että data tulee ulos samassa järjestyksessä ja liput ovat oikein.
module testipenkki;
    logic       clk = 1'b0, rst = 1'b1, push = 1'b0, pop = 1'b0;
    logic [7:0] din = '0, dout;
    logic       tyhja, taysi;
    logic [2:0] maara;
    logic       kaynnissa = 1'b1;
    int         virheita = 0;

    fifo #(.SYVYYS(4), .LEVEYS(8)) dut (.*);

    initial while (kaynnissa) #5 clk = ~clk;

    // @alku tarkista
    task automatic tarkista(input string mita, input logic ehto);
        if (!ehto) begin
            $display("VIRHE %0t: %s", $time, mita);
            virheita++;
        end
    endtask
    // @loppu tarkista

    // @alku testi
    initial begin
        @(negedge clk) rst = 1'b0;
        tarkista("tyhjä nollauksen jälkeen", tyhja && !taysi);
        // Kirjoitetaan neljä arvoa: jonon pitää olla täynnä.
        for (int i = 0; i < 4; i++) begin
            push = 1'b1; din = 8'(32'h10 + i);
            @(negedge clk);
        end
        push = 1'b0;
        tarkista("täynnä neljän kirjoituksen jälkeen", taysi);
        tarkista("määrä on 4", maara == 3'd4);
        // Luetaan kaikki takaisin.
        for (int i = 0; i < 4; i++) begin
            tarkista($sformatf("arvo %0d", i), dout == 8'(32'h10 + i));
            pop = 1'b1;
            @(negedge clk);
        end
        pop = 1'b0;
        tarkista("tyhjä lopuksi", tyhja);
        $display("ohjattu testi: %0d virhettä", virheita);
        kaynnissa = 1'b0;
        if (virheita != 0) $error("testi epäonnistui");
    end
    // @loppu testi
endmodule
