// @alku ohjelma
// Ohjelmamuisti (ROM). Käsky on 14 bittiä:
//   [13:12] käsky   0 = LI rd, vakio   1 = ADD rd, ra, rb   2 = MOV rd, ra
//   [11:10] rd   [9:8] ra   [7:6] rb   [7:0] vakio (LI)
// Ohjelma laskee Fibonaccin lukuja: r0 = 0, r1 = 1 ja toistuvasti
// r2 = r0 + r1, r0 = r1, r1 = r2.
module ohjelma (
  input  logic [3:0]  pc,
  output logic [13:0] kasky
);
  localparam logic [13:0] LI_R0_0 = {2'd0, 2'd0, 2'd0, 8'd0};
  localparam logic [13:0] LI_R1_1 = {2'd0, 2'd1, 2'd0, 8'd1};
  localparam logic [13:0] ADD_R2  = {2'd1, 2'd2, 2'd0, 2'd1, 6'd0};
  localparam logic [13:0] MOV_R0  = {2'd2, 2'd0, 2'd1, 8'd0};
  localparam logic [13:0] MOV_R1  = {2'd2, 2'd1, 2'd2, 8'd0};

  always_comb begin
    unique case (pc)
      4'd0:                        kasky = LI_R0_0;
      4'd1:                        kasky = LI_R1_1;
      4'd2, 4'd5, 4'd8, 4'd11, 4'd14: kasky = ADD_R2;
      4'd3, 4'd6, 4'd9, 4'd12, 4'd15: kasky = MOV_R0;
      4'd4, 4'd7, 4'd10, 4'd13:    kasky = MOV_R1;
    endcase
  end
endmodule
// @loppu ohjelma
