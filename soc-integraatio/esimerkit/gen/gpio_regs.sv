// Generoitu tiedostosta gpio.toml (gen/rekisterit.py). Älä muokkaa.
// Yleiskäyttöiset 8-bittiset tulot ja lähdöt
module gpio_regs
  import vaylat::*;
(
  input  logic     kello,
  input  logic     nollaus_n,
  input  apb_m2s_t apb_m,
  output apb_s2m_t apb_s,
  output logic [7:0] ulos_q,
  input  logic [7:0] sisaan_d,
  output logic [7:0] salli_q,
  input  logic [7:0] reunat_set,
  output logic [7:0] reunat_q
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
    if (!nollaus_n) ulos_q <= 8'h0;
    else if (kirjoita && apb_m.paddr == 12'h000)
      ulos_q <= 8'(sovita(32'(ulos_q), apb_m.pwdata, maski));

  always_ff @(posedge kello or negedge nollaus_n)
    if (!nollaus_n) salli_q <= 8'h0;
    else if (kirjoita && apb_m.paddr == 12'h008)
      salli_q <= 8'(sovita(32'(salli_q), apb_m.pwdata, maski));

  always_ff @(posedge kello or negedge nollaus_n)
    if (!nollaus_n) reunat_q <= 8'h0;
    else if (kirjoita && apb_m.paddr == 12'h00C)
      reunat_q <= (reunat_q & ~8'(apb_m.pwdata & maski))
              | reunat_set;
    else reunat_q <= reunat_q | reunat_set;

  // Luku. Tuntematon osoite tai kirjoitus vain luettavaan
  // rekisteriin vastaa virheellä (PSLVERR).
  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    case (apb_m.paddr)
      12'h000: begin
        apb_s.prdata  = 32'(ulos_q);
        apb_s.pslverr = 1'b0;
      end
      12'h004: begin
        apb_s.prdata  = 32'(sisaan_d);
        apb_s.pslverr = kirjoita;
      end
      12'h008: begin
        apb_s.prdata  = 32'(salli_q);
        apb_s.pslverr = 1'b0;
      end
      12'h00C: begin
        apb_s.prdata  = 32'(reunat_q);
        apb_s.pslverr = 1'b0;
      end
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

endmodule
