// CLINT-tyylinen ajastin (core-local interruptor): mtime ja mtimecmp.
//
// Ajastinkeskeytys (MTIP) on voimassa, kun mtime >= mtimecmp.
// Ohjelmisto kuittaa keskeytyksen siirtämällä vertailuarvoa eteenpäin.
// Rekisterit ovat 64-bittisiä; RV32 lukee ja kirjoittaa ne puolikkaina.
//   0x0 MTIME_L   0x4 MTIME_H   0x8 MTIMECMP_L   0xC MTIMECMP_H
module clint
  import vaylat::*;
(
  input  logic     kello,
  input  logic     nollaus_n,
  input  apb_m2s_t apb_m,
  output apb_s2m_t apb_s,
  output logic     ajastin_kesk
);

  logic [63:0] mtime, mtimecmp;
  logic        kirjoita;
  assign kirjoita = apb_m.psel && apb_m.penable && apb_m.pwrite;

  // @alku vertailu
  assign ajastin_kesk = (mtime >= mtimecmp);
  // @loppu vertailu

  always_comb begin
    apb_s        = '0;
    apb_s.pready = 1'b1;
    // Rekisterit ovat sanoja: osittainen kirjoitus on virhe.
    apb_s.pslverr = apb_m.psel && apb_m.penable && apb_m.pwrite &&
                    apb_m.pstrb != 4'b1111;
    case (apb_m.paddr)
      12'h000: apb_s.prdata = mtime[31:0];
      12'h004: apb_s.prdata = mtime[63:32];
      12'h008: apb_s.prdata = mtimecmp[31:0];
      12'h00C: apb_s.prdata = mtimecmp[63:32];
      default: apb_s.pslverr = apb_m.psel && apb_m.penable;
    endcase
  end

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      mtime    <= '0;
      mtimecmp <= '1;                  // ei keskeytystä nollauksen jälkeen
    end else begin
      mtime <= mtime + 64'd1;
      if (kirjoita)
        case (apb_m.paddr)
          12'h000: mtime[31:0]     <= apb_m.pwdata;
          12'h004: mtime[63:32]    <= apb_m.pwdata;
          12'h008: mtimecmp[31:0]  <= apb_m.pwdata;
          12'h00C: mtimecmp[63:32] <= apb_m.pwdata;
          default: ;
        endcase
    end
  end

endmodule
