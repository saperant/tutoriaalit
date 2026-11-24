// Kytkin: AXI4-Lite-väylä, jossa on useita isäntiä ja orjia.
//
// Kytkin välittää yhden siirron kerrallaan (jaettu väylä). Vapaana
// ollessaan se valitsee vuorottelevalla välittäjällä (round robin)
// yhden pyytävän isännän, dekoodaa osoitteen ja kytkee isännän
// kohdeorjaan siirron ajaksi. Osoite, jota mikään orja ei kata, ohjataan
// oletusorjalle, joka vastaa DECERR.
module kytkin
  import vaylat::*;
#(
  parameter int ISANNAT = 2,
  parameter int ORJAT   = 2,
  // Orjan i alue: (osoite & MASKI[i]) == KANTA[i].
  parameter logic [31:0] KANTA [ORJAT] = '{32'h0000_0000, 32'h1000_0000},
  parameter logic [31:0] MASKI [ORJAT] = '{32'hFFFF_C000, 32'hFFFF_0000}
)(
  input  logic      kello,
  input  logic      nollaus_n,
  input  axil_m2s_t isanta_m [ISANNAT],
  output axil_s2m_t isanta_s [ISANNAT],
  output axil_m2s_t orja_m   [ORJAT],
  input  axil_s2m_t orja_s   [ORJAT]
);

  localparam int IB = $clog2(ISANNAT);
  localparam int OB = $clog2(ORJAT + 1);
  localparam int KB = (ORJAT > 1) ? $clog2(ORJAT) : 1;
  localparam logic [OB-1:0] OLETUS = OB'(ORJAT);

  typedef enum logic [1:0] {VAPAA, LUKU, KIRJOITUS, VASTAUS} tila_t;
  tila_t          tila;
  logic [IB-1:0]  valittu, vuoro;  // nykyinen isäntä, välittäjän vuoro
  logic [OB-1:0]  kohde;
  logic           osoite_tehty, w_tehty;
  logic           oli_luku;         // oletusorjan siirto oli luku

  // @alku dekoodaus
  function automatic logic [OB-1:0] dekoodaa(input logic [31:0] osoite);
    for (int i = 0; i < ORJAT; i++)
      if ((osoite & MASKI[i]) == KANTA[i]) return OB'(i);
    return OLETUS;
  endfunction
  // @loppu dekoodaus

  // @alku valittaja
  // Vuorotteleva välittäjä: aloitetaan vuorossa olevasta isännästä ja
  // valitaan ensimmäinen, jolla on pyyntö (AR tai AW).
  logic          pyytaja_loytyi;
  logic [IB-1:0] pyytaja;
  always_comb begin
    pyytaja_loytyi = 1'b0;
    pyytaja        = vuoro;
    for (int k = 0; k < ISANNAT; k++) begin
      automatic logic [IB-1:0] i = IB'((int'(vuoro) + k) % ISANNAT);
      if (!pyytaja_loytyi &&
          (isanta_m[i].arvalid || isanta_m[i].awvalid)) begin
        pyytaja_loytyi = 1'b1;
        pyytaja        = i;
      end
    end
  end
  // @loppu valittaja

  // Oletusorjan vastaus: hyväksyy siirron ja vastaa DECERR.
  axil_s2m_t oletus_s;
  always_comb begin
    oletus_s         = '0;
    oletus_s.arready = (tila == LUKU) && !osoite_tehty;
    oletus_s.awready = (tila == KIRJOITUS) && !osoite_tehty;
    oletus_s.wready  = (tila == KIRJOITUS) && !w_tehty;
    oletus_s.rvalid  = (tila == VASTAUS) && oli_luku;
    oletus_s.bvalid  = (tila == VASTAUS) && !oli_luku;
    oletus_s.rresp   = DECERR;
    oletus_s.bresp   = DECERR;
  end

  // @alku reititys
  // Kytkentä: vain valittu isäntä näkee orjan vastaukset, ja vain
  // kohdeorja näkee isännän pyynnöt.
  axil_s2m_t kohde_s;
  always_comb begin
    kohde_s = (kohde == OLETUS) ? oletus_s : orja_s[kohde[KB-1:0]];
    for (int i = 0; i < ISANNAT; i++) begin
      isanta_s[i] = '0;
      if (tila != VAPAA && IB'(i) == valittu) isanta_s[i] = kohde_s;
    end
    for (int j = 0; j < ORJAT; j++) begin
      orja_m[j] = '0;
      if (tila != VAPAA && OB'(j) == kohde) orja_m[j] = isanta_m[valittu];
    end
  end
  // @loppu reititys

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila         <= VAPAA;
      valittu      <= '0;
      vuoro        <= '0;
      kohde        <= '0;
      osoite_tehty <= 1'b0;
      w_tehty      <= 1'b0;
      oli_luku     <= 1'b0;
    end else begin
      case (tila)
        VAPAA: if (pyytaja_loytyi) begin
          valittu <= pyytaja;
          vuoro   <= IB'((int'(pyytaja) + 1) % ISANNAT);
          oli_luku <= isanta_m[pyytaja].arvalid;
          if (isanta_m[pyytaja].arvalid) begin
            tila  <= LUKU;
            kohde <= dekoodaa(isanta_m[pyytaja].araddr);
          end else begin
            tila  <= KIRJOITUS;
            kohde <= dekoodaa(isanta_m[pyytaja].awaddr);
          end
        end
        LUKU: begin
          if (isanta_m[valittu].arvalid && kohde_s.arready)
            osoite_tehty <= 1'b1;
          if (kohde == OLETUS && osoite_tehty) tila <= VASTAUS;
          if (kohde_s.rvalid && isanta_m[valittu].rready) begin
            tila         <= VAPAA;
            osoite_tehty <= 1'b0;
          end
        end
        KIRJOITUS: begin
          if (isanta_m[valittu].awvalid && kohde_s.awready)
            osoite_tehty <= 1'b1;
          if (isanta_m[valittu].wvalid && kohde_s.wready)
            w_tehty <= 1'b1;
          if (kohde == OLETUS && osoite_tehty && w_tehty)
            tila <= VASTAUS;
          if (kohde_s.bvalid && isanta_m[valittu].bready) begin
            tila         <= VAPAA;
            osoite_tehty <= 1'b0;
            w_tehty      <= 1'b0;
          end
        end
        VASTAUS:                        // oletusorja vastaa
          if ((oletus_s.rvalid && isanta_m[valittu].rready) ||
              (oletus_s.bvalid && isanta_m[valittu].bready)) begin
            tila         <= VAPAA;
            osoite_tehty <= 1'b0;
            w_tehty      <= 1'b0;
          end
        default: tila <= VAPAA;
      endcase
    end
  end

endmodule
