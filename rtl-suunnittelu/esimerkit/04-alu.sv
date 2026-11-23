// @alku alu
typedef enum logic [2:0] {
  OP_ADD, OP_SUB, OP_AND, OP_OR, OP_XOR, OP_SLT, OP_SLL, OP_SRL
} alu_op_t;

module alu #(
  parameter int W = 16
) (
  input  alu_op_t      op,
  input  logic [W-1:0] a,
  input  logic [W-1:0] b,
  output logic [W-1:0] tulos,
  output logic         nolla,
  output logic         ylivuoto   // etumerkillinen ylivuoto (ADD, SUB)
);
  localparam int SW = $clog2(W);   // siirtomäärän bitit

  always_comb begin
    ylivuoto = 1'b0;               // oletusarvot ensin: ei salpoja
    unique case (op)
      OP_ADD: begin
        tulos    = a + b;
        ylivuoto = (a[W-1] == b[W-1]) && (tulos[W-1] != a[W-1]);
      end
      OP_SUB: begin
        tulos    = a - b;
        ylivuoto = (a[W-1] != b[W-1]) && (tulos[W-1] != a[W-1]);
      end
      OP_AND:  tulos = a & b;
      OP_OR:   tulos = a | b;
      OP_XOR:  tulos = a ^ b;
      OP_SLT:  tulos = W'($signed(a) < $signed(b));
      OP_SLL:  tulos = a << b[SW-1:0];
      OP_SRL:  tulos = a >> b[SW-1:0];
    endcase
  end

  assign nolla = (tulos == '0);
endmodule
// @loppu alu

// @alku testipenkki
module testipenkki;
  logic [15:0] a, b, tulos;
  logic        nolla, ylivuoto;
  alu_op_t     op;
  int          virheita = 0;

  alu #(.W(16)) dut (.op, .a, .b, .tulos, .nolla, .ylivuoto);

  task automatic koe(alu_op_t o, logic [15:0] x, logic [15:0] y,
                     logic [15:0] odotettu, logic odotettu_yv);
    op = o;
    a  = x;
    b  = y;
    #1;
    if (tulos !== odotettu || ylivuoto !== odotettu_yv) begin
      virheita++;
      $display("VIRHE: %s %h %h -> %h yv=%b", o.name(), x, y, tulos,
               ylivuoto);
    end
  endtask

  initial begin
    koe(OP_ADD, 16'd1200, 16'd34, 16'd1234, 1'b0);
    koe(OP_ADD, 16'h7FFF, 16'h0001, 16'h8000, 1'b1);  // + + -> -
    koe(OP_SUB, 16'h8000, 16'h0001, 16'h7FFF, 1'b1);  // - + -> +
    koe(OP_SUB, 16'd5, 16'd7, 16'hFFFE, 1'b0);
    koe(OP_SLT, 16'hFFFF, 16'd1, 16'd1, 1'b0);        // -1 < 1
    koe(OP_SLL, 16'h0F0F, 16'd4, 16'hF0F0, 1'b0);
    koe(OP_SRL, 16'h8000, 16'd15, 16'h0001, 1'b0);
    koe(OP_XOR, 16'hAAAA, 16'hAAAA, 16'h0000, 1'b0);
    if (!nolla) begin
      virheita++;
      $display("VIRHE: nolla-lippu");
    end
    $display("ALU: 8 koetta, %0d virhettä", virheita);
    if (virheita != 0) $fatal(1, "ALU laskee väärin");
  end
endmodule
// @loppu testipenkki
