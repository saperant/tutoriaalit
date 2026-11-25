// opetus.lib-kirjaston solujen toiminnalliset mallit porttitason
// simulointiin (ilman viiveitä). Tuotantokirjaston mukana tulevat
// vastaavat mallit, usein ajoituksineen (specify-lohkot).
// @alku mallit
module INV_X1   (input A, output Y);         assign Y = ~A;          endmodule
module BUF_X1   (input A, output Y);         assign Y = A;           endmodule
module BUF_X4   (input A, output Y);         assign Y = A;           endmodule
module NAND2_X1 (input A, B, output Y);      assign Y = ~(A & B);    endmodule
module NOR2_X1  (input A, B, output Y);      assign Y = ~(A | B);    endmodule
module AND2_X1  (input A, B, output Y);      assign Y = A & B;       endmodule
module OR2_X1   (input A, B, output Y);      assign Y = A | B;       endmodule
module XOR2_X1  (input A, B, output Y);      assign Y = A ^ B;       endmodule
module XNOR2_X1 (input A, B, output Y);      assign Y = ~(A ^ B);    endmodule
module AOI21_X1 (input A1, A2, B, output Y);
  assign Y = ~((A1 & A2) | B);
endmodule
module OAI21_X1 (input A1, A2, B, output Y);
  assign Y = ~((A1 | A2) & B);
endmodule
module MUX2_X1  (input A, B, S, output Y);   assign Y = S ? B : A;   endmodule
module DFF_X1 (input D, CK, output reg Q);
  always @(posedge CK) Q <= D;
endmodule
module SDFF_X1 (input D, SI, SE, CK, output reg Q);
  always @(posedge CK) Q <= SE ? SI : D;
endmodule
module DFFR_X1 (input D, RN, CK, output reg Q);
  always @(posedge CK or negedge RN) Q <= !RN ? 1'b0 : D;
endmodule
// @loppu mallit
