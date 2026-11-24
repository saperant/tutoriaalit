// Ohjainlohko, jossa on tarkoituksellisia lint-varoituksia: luvun 6
// sallittujen varoitusten lista hyväksyy niistä yhden perusteluineen.
module ohjain (
  input  logic       clk,
  input  logic       rst_n,
  input  logic [7:0] data,
  input  logic       testi,    // varattu tuotantotestille
  output logic [3:0] tila
);
  logic [7:0] summa;

  assign summa = {1'b0, data[6:0]} + 8'd1;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) tila <= '0;
    else        tila <= summa;
  end
endmodule
