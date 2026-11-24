// APB4-isannan tehtavat testipenkeille. Sisallytetaan moduulin sisaan,
// jossa on signaalit clk, psel, penable, pwrite, paddr, pwdata,
// prdata, pready ja pslverr seka muuttujat virheet ja vaylavirhe.
//
// Testipenkki ohjaa ja lukee signaaleja kellon laskevalla reunalla,
// jolloin ne ovat vakaat eika testipenkki kilpaile piirin kanssa
// nousevalla reunalla.

typedef logic [$bits(paddr)-1:0] osoite_t;

// @alku apb
task automatic siirto(input logic kirj, input osoite_t osoite,
                      input logic [31:0] wdata,
                      output logic [31:0] rdata);
    @(negedge clk);                       // asetusvaihe
    psel = 1; pwrite = kirj; paddr = osoite; pwdata = wdata;
    @(negedge clk);                       // siirtovaihe
    penable = 1;
    #1;
    while (!pready) begin
        @(negedge clk);
        #1;
    end
    rdata = prdata;                       // siirto paattyy seuraavalla
    vaylavirhe = pslverr;                 // nousevalla reunalla
    @(negedge clk);
    psel = 0; penable = 0;
endtask
// @loppu apb

task automatic kirjoita(input osoite_t osoite, input logic [31:0] data);
    /* verilator lint_off UNUSEDSIGNAL */
    logic [31:0] ohita;
    /* verilator lint_on UNUSEDSIGNAL */
    siirto(1, osoite, data, ohita);
endtask

task automatic lue(input osoite_t osoite, output logic [31:0] data);
    siirto(0, osoite, 32'h0, data);
endtask

function automatic void raportoi(input logic ok, input string teksti);
    $display("%s %s", ok ? "OK   " : "VIRHE", teksti);
    if (!ok) virheet++;
endfunction

// @alku odota
task automatic odota(input osoite_t osoite, input logic [31:0] odotettu,
                     input string kuvaus);
    logic [31:0] data;
    lue(osoite, data);
    raportoi(data === odotettu && !vaylavirhe,
             $sformatf("%h  %s", data, kuvaus));
endtask

task automatic kielletty(input osoite_t osoite, input string kuvaus);
    kirjoita(osoite, 32'hFFFF_FFFF);
    raportoi(vaylavirhe, $sformatf("PSLVERR   %s", kuvaus));
endtask
// @loppu odota

function automatic void huomio(input string teksti);
    $display("                %s", teksti);
endfunction
