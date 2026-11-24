// @alku muisti
// 256 x 8 bitin muisti, yksi kirjoitus- ja yksi lukuportti.
// SYNKRONINEN = 1: luku rekisteröidään, joten synteesi voi käyttää
// lohko-RAMia. SYNKRONINEN = 0: luku on kombinatorinen, mihin iCE40:n
// lohko-RAM ei pysty, joten muisti rakentuu kiikuista ja
// multipleksereistä.
module muisti #(
  parameter bit SYNKRONINEN = 1'b1
) (
  input  logic       clk,
  input  logic       kirjoita,
  input  logic [7:0] kirjoitusosoite,
  input  logic [7:0] tieto_sisaan,
  input  logic [7:0] lukuosoite,
  output logic [7:0] tieto_ulos
);
  logic [7:0] sisalto [256];

  always_ff @(posedge clk)
    if (kirjoita) sisalto[kirjoitusosoite] <= tieto_sisaan;

  if (SYNKRONINEN) begin : g_synkroninen
    always_ff @(posedge clk) tieto_ulos <= sisalto[lukuosoite];
  end else begin : g_kombinatorinen
    assign tieto_ulos = sisalto[lukuosoite];
  end
endmodule
// @loppu muisti
