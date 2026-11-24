// UART-lähetin APB-orjana (8N1: aloitusbitti, 8 databittiä LSB ensin,
// lopetusbitti).
//
// Rekisterit:
//   0x0 DATA    kirjoitus aloittaa lähetyksen (ohitetaan, jos varattu)
//   0x4 TILA    bitti 0: lähetys käynnissä
//   0x8 JAKAJA  kellojaksoja bittiä kohden (nollausarvo 8)
module uart
  import vaylat::*;
(
  input  logic     kello,
  input  logic     nollaus_n,
  input  apb_m2s_t apb_m,
  output apb_s2m_t apb_s,
  output logic     tx
);

  logic [15:0] jakaja, laskuri;
  logic [9:0]  siirto;        // lopetusbitti, data, aloitusbitti
  logic [3:0]  bitit;         // jäljellä olevat bitit
  logic        varattu, kirjoita;

  assign varattu  = (bitit != 4'd0);
  assign kirjoita = apb_m.psel && apb_m.penable && apb_m.pwrite;
  assign tx       = varattu ? siirto[0] : 1'b1;

  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    // Rekisterit ovat sanoja: osittainen kirjoitus on virhe.
    apb_s.pslverr = apb_m.psel && apb_m.penable && apb_m.pwrite &&
                    apb_m.pstrb != 4'b1111;
    case (apb_m.paddr)
      12'h000: ;
      12'h004: apb_s.prdata = {31'd0, varattu};
      12'h008: apb_s.prdata = {16'd0, jakaja};
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      jakaja  <= 16'd8;
      laskuri <= '0;
      siirto  <= '1;
      bitit   <= '0;
    end else begin
      if (kirjoita && apb_m.paddr == 12'h008)
        jakaja <= apb_m.pwdata[15:0];
      if (kirjoita && apb_m.paddr == 12'h000 && !varattu) begin
        siirto  <= {1'b1, apb_m.pwdata[7:0], 1'b0};
        bitit   <= 4'd10;
        laskuri <= jakaja - 16'd1;
      end else if (varattu) begin
        if (laskuri == 16'd0) begin
          siirto  <= {1'b1, siirto[9:1]};
          bitit   <= bitit - 4'd1;
          laskuri <= jakaja - 16'd1;
        end else begin
          laskuri <= laskuri - 16'd1;
        end
      end
    end
  end

endmodule
