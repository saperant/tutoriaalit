// Parametroitu laskuri: vuon synteesi- ja lint-kohde.
module laskuri #(
  parameter int LEVEYS = 8
) (
  input  logic              clk,
  input  logic              rst_n,
  input  logic              sallittu,
  output logic [LEVEYS-1:0] arvo,
  output logic              yli
);
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      arvo <= '0;
      yli  <= 1'b0;
    end else if (sallittu) begin
      {yli, arvo} <= {1'b0, arvo} + 1'b1;
    end
  end
endmodule
