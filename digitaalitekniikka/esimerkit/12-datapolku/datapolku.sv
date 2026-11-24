// @alku datapolku
// Pieni datapolku: ohjelmalaskuri, käskyn dekoodaus, rekisteritiedosto
// ja summain. Jokainen käsky suoritetaan yhdessä kellojaksossa: luku
// rekistereistä, laskenta ja kirjoitus tapahtuvat saman jakson aikana,
// ja kellon reuna tallentaa tuloksen ja seuraavan PC:n.
module datapolku (
  input  logic       clk,
  input  logic       nollaa,
  output logic [3:0] pc,
  output logic [1:0] rd,
  output logic [7:0] tulos
);
  logic [13:0] kasky;
  logic [1:0]  op, ra, rb;
  logic [7:0]  vakio, a, b;
  logic [7:0]  r [4];

  ohjelma u_ohjelma (.pc, .kasky);

  // Käskyn kentät (dekoodaus on pelkkää johdotusta).
  assign op    = kasky[13:12];
  assign rd    = kasky[11:10];
  assign ra    = kasky[9:8];
  assign rb    = kasky[7:6];
  assign vakio = kasky[7:0];

  // Lukuportit ja ALU: multiplekseri valitsee tuloksen lähteen.
  assign a = r[ra];
  assign b = r[rb];
  always_comb begin
    unique case (op)
      2'd0:    tulos = vakio;       // LI
      2'd1:    tulos = a + b;       // ADD
      default: tulos = a;           // MOV
    endcase
  end

  always_ff @(posedge clk) begin
    if (nollaa) begin
      pc <= '0;
    end else begin
      r[rd] <= tulos;               // kirjoitusportti
      pc    <= pc + 1'b1;
    end
  end
endmodule
// @loppu datapolku
