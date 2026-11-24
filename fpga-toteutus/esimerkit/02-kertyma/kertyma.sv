// @alku kertyma
// Kertymä: lisää joka kellojaksolla tulon x summaan. 16-bittinen
// summain kuvautuu FPGA:ssa logiikkasolujen kantoketjuun.
module kertyma #(
  parameter int LEVEYS = 16
) (
  input  logic              clk,
  input  logic              tyhjenna,
  input  logic [7:0]        x,
  output logic [LEVEYS-1:0] summa
);
  always_ff @(posedge clk) begin
    if (tyhjenna) summa <= '0;
    else          summa <= summa + LEVEYS'(x);
  end
endmodule
// @loppu kertyma
