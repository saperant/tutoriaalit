// DMA-ohjain: kopioi sanoja muistista toiseen ilman suoritinta.
//
// Ohjelmisto asettaa rekisterit APB:n kautta ja käynnistää siirron.
// Ohjain on itse AXI4-Lite-isäntä: se lukee sanan lähteestä, kirjoittaa
// sen kohteeseen ja jatkaa, kunnes MAARA sanaa on siirretty.
//   0x00 LAHDE   0x04 KOHDE   0x08 MAARA (sanoja)
//   0x0C OHJAUS  bitti 0: käynnistä (pulssi), bitti 1: keskeytys sallittu
//   0x10 TILA    bitti 0: käynnissä, bitti 1: valmis (W1C),
//                bitti 2: väylävirhe (W1C)
module dma
  import vaylat::*;
(
  input  logic      kello,
  input  logic      nollaus_n,
  input  apb_m2s_t  apb_m,
  output apb_s2m_t  apb_s,
  output axil_m2s_t m,
  input  axil_s2m_t s,
  output logic      keskeytys
);

  typedef enum logic [2:0] {VAPAA, LUE, ODOTA_R, KIRJOITA, ODOTA_B}
    tila_t;
  tila_t       tila;
  logic [31:0] lahde, kohde, maara, data;
  logic        salli_kesk, valmis, virhe, aw_tehty, w_tehty;
  logic        kirjoita_reg;

  assign kirjoita_reg = apb_m.psel && apb_m.penable && apb_m.pwrite;
  assign keskeytys    = salli_kesk && (valmis || virhe);

  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    // Rekisterit ovat sanoja: osittainen kirjoitus on virhe.
    apb_s.pslverr = apb_m.psel && apb_m.penable && apb_m.pwrite &&
                    apb_m.pstrb != 4'b1111;
    case (apb_m.paddr)
      12'h000: apb_s.prdata = lahde;
      12'h004: apb_s.prdata = kohde;
      12'h008: apb_s.prdata = maara;
      12'h00C: apb_s.prdata = {30'd0, salli_kesk, 1'b0};
      12'h010: apb_s.prdata = {29'd0, virhe, valmis, tila != VAPAA};
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

  // @alku isanta
  always_comb begin
    m         = '0;
    m.araddr  = lahde;
    m.arvalid = (tila == LUE);
    m.rready  = (tila == ODOTA_R);
    m.awaddr  = kohde;
    m.awvalid = (tila == KIRJOITA) && !aw_tehty;
    m.wdata   = data;
    m.wstrb   = 4'b1111;
    m.wvalid  = (tila == KIRJOITA) && !w_tehty;
    m.bready  = (tila == ODOTA_B);
  end
  // @loppu isanta

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila       <= VAPAA;
      lahde      <= '0;
      kohde      <= '0;
      maara      <= '0;
      data       <= '0;
      salli_kesk <= 1'b0;
      valmis     <= 1'b0;
      virhe      <= 1'b0;
      aw_tehty   <= 1'b0;
      w_tehty    <= 1'b0;
    end else begin
      // Rekisterit ovat kirjoitettavissa vain, kun siirto ei ole käynnissä.
      if (kirjoita_reg && tila == VAPAA)
        case (apb_m.paddr)
          12'h000: lahde <= apb_m.pwdata;
          12'h004: kohde <= apb_m.pwdata;
          12'h008: maara <= apb_m.pwdata;
          12'h00C: begin
            salli_kesk <= apb_m.pwdata[1];
            if (apb_m.pwdata[0] && maara != 32'd0) tila <= LUE;
          end
          default: ;
        endcase
      if (kirjoita_reg && apb_m.paddr == 12'h010) begin
        if (apb_m.pwdata[1]) valmis <= 1'b0;
        if (apb_m.pwdata[2]) virhe  <= 1'b0;
      end
      // @alku siirto
      case (tila)
        LUE:     if (s.arready) tila <= ODOTA_R;
        ODOTA_R: if (s.rvalid) begin
          data <= s.rdata;
          if (s.rresp[1]) begin virhe <= 1'b1; tila <= VAPAA; end
          else tila <= KIRJOITA;
        end
        KIRJOITA: begin
          if (m.awvalid && s.awready) aw_tehty <= 1'b1;
          if (m.wvalid && s.wready)   w_tehty  <= 1'b1;
          if ((aw_tehty || s.awready) && (w_tehty || s.wready))
            tila <= ODOTA_B;
        end
        ODOTA_B: if (s.bvalid) begin
          aw_tehty <= 1'b0;
          w_tehty  <= 1'b0;
          if (s.bresp[1]) begin
            virhe <= 1'b1;
            tila  <= VAPAA;
          end else begin
            lahde <= lahde + 32'd4;
            kohde <= kohde + 32'd4;
            maara <= maara - 32'd1;
            if (maara == 32'd1) begin
              valmis <= 1'b1;
              tila   <= VAPAA;
            end else tila <= LUE;
          end
        end
        default: ;
      endcase
      // @loppu siirto
    end
  end

endmodule
