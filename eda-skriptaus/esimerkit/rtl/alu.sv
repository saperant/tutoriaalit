// Pieni ALU. Makro VIKA lisää tarkoituksellisen virheen, jonka
// regressio löytää vain osalla siemenistä.
module alu (
  input  logic [1:0] op,      // 0 ADD, 1 SUB, 2 AND, 3 XOR
  input  logic [7:0] a,
  input  logic [7:0] b,
  output logic [7:0] y
);
  always_comb begin
    unique case (op)
      2'd0: y = a + b;
      2'd1: y = a - b;
      2'd2: y = a & b;
`ifdef VIKA
      2'd3: y = (a[7] & b[7]) ? (a | b) : (a ^ b);
`else
      2'd3: y = a ^ b;
`endif
      default: y = '0;
    endcase
  end
endmodule
