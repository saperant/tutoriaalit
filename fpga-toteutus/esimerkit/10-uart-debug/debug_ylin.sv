// @alku debug
// Virheenjäljitysydin: isäntä lukee ja kirjoittaa rekistereitä UARTin
// yli. Komennot: 'L' osoite -> vastaus arvo; 'K' osoite arvo -> 'K'.
// Rekisterit 0-3 ovat luettavia ja kirjoitettavia, 4 on vapaasti käyvä
// laskuri ja 5 tunniste 0x42. Rekisterin 0 alin bitti ohjaa lediä.
module debug_ylin #(
  parameter int KELLOT_PER_BITTI = 104
) (
  input  logic clk,
  input  logic rx,
  output logic tx,
  output logic led_n
);
// @loppu debug
  logic       rx_kelpaa, tx_laheta = 1'b0, tx_valmis;
  logic [7:0] rx_tavu, tx_tavu = '0;
  logic [7:0] rekisterit [4];
  initial for (int i = 0; i < 4; i++) rekisterit[i] = '0;
  logic [7:0] laskuri = '0;

  uart_rx #(.KELLOT_PER_BITTI(KELLOT_PER_BITTI)) vastaanotin (
    .clk, .rx, .kelpaa(rx_kelpaa), .tavu(rx_tavu));
  uart_tx #(.KELLOT_PER_BITTI(KELLOT_PER_BITTI)) lahetin (
    .clk, .laheta(tx_laheta), .tavu(tx_tavu), .valmis(tx_valmis), .tx);

// @alku tilakone
  typedef enum logic [1:0] {ODOTA, OSOITE, ARVO} tila_t;
  tila_t      tila = ODOTA;
  logic       kirjoitus = 1'b0;
  logic [2:0] osoite = '0;

  function automatic logic [7:0] lue(input logic [2:0] o);
    case (o)
      3'd4:    lue = laskuri;
      3'd5:    lue = 8'h42;
      default: lue = o[2] ? 8'h00 : rekisterit[o[1:0]];
    endcase
  endfunction

  always_ff @(posedge clk) begin
    laskuri   <= laskuri + 1'b1;
    tx_laheta <= 1'b0;
    // Isäntä odottaa vastauksen ennen seuraavaa komentoa; tavu, joka
    // saapuu lähetyksen aikana, hylätään.
    if (rx_kelpaa && tx_valmis) begin
      case (tila)
        ODOTA: begin
          kirjoitus <= rx_tavu == "K";
          if (rx_tavu == "K" || rx_tavu == "L") tila <= OSOITE;
        end
        OSOITE: begin
          osoite <= rx_tavu[2:0];
          if (kirjoitus) begin
            tila <= ARVO;
          end else begin
            tx_tavu   <= lue(rx_tavu[2:0]);
            tx_laheta <= 1'b1;
            tila      <= ODOTA;
          end
        end
        ARVO: begin
          if (!osoite[2]) rekisterit[osoite[1:0]] <= rx_tavu;
          tx_tavu   <= "K";
          tx_laheta <= 1'b1;
          tila      <= ODOTA;
        end
        default: tila <= ODOTA;
      endcase
    end
  end
// @loppu tilakone

  assign led_n = ~rekisterit[0][0];
endmodule
