// Generoitu tiedostosta syscon.json (gen/rekisterit.py). Älä muokkaa.
// Järjestelmäohjain: tunniste, apurekisteri ja lopetus
module syscon_regs
  import vaylat::*;
(
  input  logic     kello,
  input  logic     nollaus_n,
  input  apb_m2s_t apb_m,
  output apb_s2m_t apb_s,
  output logic [31:0] apu_q,
  output logic [7:0] lopeta_q,
  output logic lopeta_we
);

  // Kirjoitus tapahtuu APB:n ACCESS-vaiheessa; PSTRB rajaa tavut.
  logic        kirjoita;
  logic [31:0] maski;
  assign kirjoita = apb_m.psel && apb_m.penable && apb_m.pwrite;
  assign maski = {{8{apb_m.pstrb[3]}}, {8{apb_m.pstrb[2]}},
                  {8{apb_m.pstrb[1]}}, {8{apb_m.pstrb[0]}}};

  function automatic logic [31:0] sovita(input logic [31:0] vanha,
                                        input logic [31:0] uusi,
                                        input logic [31:0] m);
    return (vanha & ~m) | (uusi & m);
  endfunction

  always_ff @(posedge kello or negedge nollaus_n)
    if (!nollaus_n) apu_q <= 32'h0;
    else if (kirjoita && apb_m.paddr == 12'h004)
      apu_q <= 32'(sovita(32'(apu_q), apb_m.pwdata, maski));

  assign lopeta_we = kirjoita && apb_m.paddr == 12'h008;
  assign lopeta_q  = apb_m.pwdata[7:0];

  // Luku. Tuntematon osoite tai kirjoitus vain luettavaan
  // rekisteriin vastaa virheellä (PSLVERR).
  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    case (apb_m.paddr)
      12'h000: begin
        apb_s.prdata  = 32'(32'h534F4331);
        apb_s.pslverr = kirjoita;
      end
      12'h004: begin
        apb_s.prdata  = 32'(apu_q);
        apb_s.pslverr = 1'b0;
      end
      12'h008: begin
        apb_s.prdata  = 32'('0);
        apb_s.pslverr = 1'b0;
      end
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

endmodule
