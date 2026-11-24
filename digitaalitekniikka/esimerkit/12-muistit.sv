// ROM taulukkona ja rekisteritiedosto, jossa on kaksi lukuporttia.

// @alku rom
// Seitsensegmenttinäytön dekooderi ROM-muistina: osoite on numero,
// data kertoo, mitkä segmentit (gfedcba) palavat. Mikä tahansa
// kombinaatiologiikka voidaan toteuttaa näin: totuustaulu muistissa.
module segmentti_rom (
  input  logic [3:0] numero,
  output logic [6:0] segmentit
);
  localparam logic [6:0] ROM [16] = '{
    7'h3F, 7'h06, 7'h5B, 7'h4F, 7'h66, 7'h6D, 7'h7D, 7'h07,   // 0–7
    7'h7F, 7'h6F, 7'h77, 7'h7C, 7'h39, 7'h5E, 7'h79, 7'h71    // 8–F
  };
  assign segmentit = ROM[numero];
endmodule
// @loppu rom

// @alku rekisteritiedosto
// Neljä 8-bittistä rekisteriä. Kaksi lukuporttia (asynkroninen luku)
// ja yksi kirjoitusportti (kellon reunalla), kuten suorittimen
// rekisteritiedostossa: käsky lukee kaksi operandia ja kirjoittaa yhden
// tuloksen.
module rekisteritiedosto (
  input  logic       clk,
  input  logic       kirjoita,
  input  logic [1:0] k_osoite,
  input  logic [7:0] k_data,
  input  logic [1:0] osoite_a,
  input  logic [1:0] osoite_b,
  output logic [7:0] data_a,
  output logic [7:0] data_b
);
  logic [7:0] rekisterit [4];

  always_ff @(posedge clk) begin
    if (kirjoita) rekisterit[k_osoite] <= k_data;
  end

  assign data_a = rekisterit[osoite_a];
  assign data_b = rekisterit[osoite_b];
endmodule
// @loppu rekisteritiedosto

// @alku testipenkki
module testipenkki;
  logic [3:0] numero;
  logic [6:0] segmentit;
  logic       clk = 1'b0, kaynnissa = 1'b1, kirjoita = 1'b0;
  logic [1:0] k_osoite = '0, osoite_a = '0, osoite_b = '0;
  logic [7:0] k_data = '0, data_a, data_b;

  segmentti_rom     u_rom (.numero, .segmentit);
  rekisteritiedosto u_rf  (.clk, .kirjoita, .k_osoite, .k_data,
                           .osoite_a, .osoite_b, .data_a, .data_b);

  initial while (kaynnissa) #5 clk = ~clk;

  // Näyttää numeron seitsensegmenttinäytön segmentteinä.
  task automatic piirra(logic [6:0] s);
    $display(" %s ", s[0] ? "_" : " ");
    $display("%s%s%s", s[5] ? "|" : " ", s[6] ? "_" : " ",
             s[1] ? "|" : " ");
    $display("%s%s%s", s[4] ? "|" : " ", s[3] ? "_" : " ",
             s[2] ? "|" : " ");
  endtask

  initial begin
    numero = 4'd2; #1 piirra(segmentit);
    numero = 4'hE; #1 piirra(segmentit);

    // Kirjoitetaan r1 = 42 ja r2 = 7, luetaan molemmat yhtä aikaa.
    @(negedge clk);
    kirjoita = 1'b1; k_osoite = 2'd1; k_data = 8'd42;
    @(negedge clk);
    k_osoite = 2'd2; k_data = 8'd7;
    @(negedge clk);
    kirjoita = 1'b0; osoite_a = 2'd1; osoite_b = 2'd2;
    #1 $display("r1 = %0d, r2 = %0d", data_a, data_b);
    kaynnissa = 1'b0;
  end
endmodule
// @loppu testipenkki
