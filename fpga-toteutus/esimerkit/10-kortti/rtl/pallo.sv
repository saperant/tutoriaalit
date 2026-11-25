// @alku pallo
// Pallon paikka päivittyy kerran kehyksessä ja kimpoaa alueen reunoista.
// Paikka on pallon vasen yläkulma.
module pallo #(
  parameter int KOKO = 32,
  parameter int X_MIN = 8,   X_MAX = 632,
  parameter int Y_MIN = 128, Y_MAX = 368,
  parameter int VX = 6, VY = 4
) (
  input  logic       clk,
  input  logic       nollaus,
  input  logic       kehys,
  input  logic       pysayta,
  output logic [9:0] px,
  output logic [9:0] py
);
  logic oikealle = 1'b1, alas = 1'b1;

  initial begin px = 10'(X_MIN + 40); py = 10'(Y_MIN + 20); end

  always_ff @(posedge clk)
    if (nollaus) begin
      px <= 10'(X_MIN + 40);
      py <= 10'(Y_MIN + 20);
      oikealle <= 1'b1;
      alas     <= 1'b1;
    end else if (kehys && !pysayta) begin
      if (oikealle) begin
        if (px >= 10'(X_MAX - KOKO - VX)) oikealle <= 1'b0;
        else                              px <= px + 10'(VX);
      end else begin
        if (px <= 10'(X_MIN + VX)) oikealle <= 1'b1;
        else                       px <= px - 10'(VX);
      end
      if (alas) begin
        if (py >= 10'(Y_MAX - KOKO - VY)) alas <= 1'b0;
        else                              py <= py + 10'(VY);
      end else begin
        if (py <= 10'(Y_MIN + VY)) alas <= 1'b1;
        else                       py <= py - 10'(VY);
      end
    end
endmodule
// @loppu pallo
