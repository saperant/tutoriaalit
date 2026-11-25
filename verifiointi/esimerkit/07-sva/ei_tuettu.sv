// Sekvenssin viivettä ## ei tueta Verilatorin versiossa 5.020. Tämä
// tiedosto näyttää, miltä virheilmoitus näyttää (luku 7).
module ei_tuettu (input logic clk, pyynto, kuittaus);
    a_kuittaus: assert property (@(posedge clk)
        pyynto |-> ##[1:3] kuittaus);
endmodule
