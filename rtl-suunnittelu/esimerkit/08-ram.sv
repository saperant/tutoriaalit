// @alku ram
// Kaksiporttinen RAM: yksi kirjoitusportti, yksi lukuportti, sama kello.
// Rekisteröity luku (latenssi 1) on kuvio, jonka synteesityökalut
// tunnistavat ja sijoittavat FPGA:n lohkomuistiin (block RAM).
module ram_2p #(
  parameter int W = 8,                // sanan leveys
  parameter int D = 256               // sanojen määrä
) (
  input  logic                 clk,
  input  logic                 kirjoita,
  input  logic [$clog2(D)-1:0] k_osoite,
  input  logic [W-1:0]         k_data,
  input  logic [$clog2(D)-1:0] l_osoite,
  output logic [W-1:0]         l_data
);
  logic [W-1:0] muisti [D];           // ei nollausta: muisti ei nollaudu

  always_ff @(posedge clk) begin
    if (kirjoita) muisti[k_osoite] <= k_data;
    l_data <= muisti[l_osoite];       // vanha arvo, jos sama osoite
  end
endmodule
// @loppu ram

// @alku rom
// ROM: sisältö lasketaan käännösaikana funktiolla. Tässä 8-bittinen
// siniaallon neljännes; sama onnistuu tiedostosta $readmemh:lla.
module sini_rom (
  input  logic       clk,
  input  logic [5:0] osoite,
  output logic [7:0] arvo
);
  function automatic logic [7:0] sini(int i);
    return 8'($rtoi(255.0 * $sin(3.14159265 / 2.0 * i / 64.0) + 0.5));
  endfunction

  logic [7:0] taulu [64];
  initial for (int i = 0; i < 64; i++) taulu[i] = sini(i);

  always_ff @(posedge clk) arvo <= taulu[osoite];
endmodule
// @loppu rom

module testipenkki;
  logic       clk = 1'b0, kaynnissa = 1'b1;
  logic       kirjoita = 1'b0;
  logic [7:0] k_osoite = '0, l_osoite = '0, k_data = '0, l_data;
  logic [5:0] r_osoite = '0;
  logic [7:0] r_arvo;

  ram_2p #(.W(8), .D(256)) u_ram (.clk, .kirjoita, .k_osoite, .k_data,
                                  .l_osoite, .l_data);
  sini_rom u_rom (.clk, .osoite(r_osoite), .arvo(r_arvo));

  initial while (kaynnissa) #5 clk = ~clk;

  initial begin
    #1;
    for (int i = 0; i < 256; i++) begin   // täytetään: data = 3*i
      kirjoita = 1'b1;
      k_osoite = 8'(i);
      k_data   = 8'(3 * i);
      @(posedge clk); #1;
    end
    kirjoita = 1'b0;
    l_osoite = 8'd100;
    #1 $display("ennen reunaa: l_data = %0d (edellinen luku)", l_data);
    @(posedge clk); #1;
    $display("reunan jälkeen: muisti[100] = %0d", l_data);
    // Luku ja kirjoitus samaan osoitteeseen samalla reunalla.
    kirjoita = 1'b1;
    k_osoite = 8'd100;
    k_data   = 8'd7;
    @(posedge clk); #1;
    kirjoita = 1'b0;
    $display("samanaikainen kirjoitus: luettiin vanha %0d", l_data);
    @(posedge clk); #1;
    $display("seuraavalla jaksolla: %0d", l_data);
    for (int i = 0; i < 64; i += 21) begin
      r_osoite = 6'(i);
      @(posedge clk); #1;
      $display("sini_rom[%2d] = %3d", i, r_arvo);
    end
    if (l_data != 8'd7) $fatal(1, "RAM väärin");
    kaynnissa = 1'b0;
  end
endmodule
