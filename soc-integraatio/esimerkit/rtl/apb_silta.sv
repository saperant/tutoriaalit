// APB-silta: AXI4-Lite-orja → APB-isäntä hitaille oheislaitteille.
//
// Sillan alue on jaettu 4 KiB:n ikkunoihin: osoitteen bitit 15:12
// valitsevat oheislaitteen (PSEL). Ikkuna, jossa ei ole oheislaitetta,
// vastaa DECERR. Jokainen APB-siirto kestää vähintään kaksi kellojaksoa:
// SETUP (PSEL) ja ACCESS (PSEL ja PENABLE), joka jatkuu PREADYyn asti.
module apb_silta
  import vaylat::*;
#(
  parameter int LAITTEET = 6
)(
  input  logic      kello,
  input  logic      nollaus_n,
  input  axil_m2s_t m,
  output axil_s2m_t s,
  output apb_m2s_t  apb_m [LAITTEET],
  input  apb_s2m_t  apb_s [LAITTEET]
);

  typedef enum logic [1:0] {VAPAA, SETUP, ACCESS, VASTAUS} tila_t;
  tila_t       tila;
  logic        kirjoitus;
  logic [15:0] osoite;
  logic [31:0] kdata, ldata;
  logic [3:0]  tavut;
  logic [1:0]  vastaus;
  logic [3:0]  laite;
  logic        laite_ok;

  assign laite    = osoite[15:12];
  assign laite_ok = int'(laite) < LAITTEET;

  // @alku apb
  always_comb begin
    for (int i = 0; i < LAITTEET; i++) begin
      apb_m[i]         = '0;
      apb_m[i].paddr   = osoite[11:0];
      apb_m[i].pwrite  = kirjoitus;
      apb_m[i].pwdata  = kdata;
      apb_m[i].pstrb   = kirjoitus ? tavut : 4'b0000;
      apb_m[i].psel    = (tila == SETUP || tila == ACCESS) &&
                         laite_ok && laite == 4'(i);
      apb_m[i].penable = (tila == ACCESS);
    end
  end
  // @loppu apb

  // AXI4-Lite-puoli: yksi siirto kerrallaan.
  always_comb begin
    s         = '0;
    s.arready = (tila == VAPAA) && !(m.awvalid && m.wvalid);
    s.awready = (tila == VAPAA) && m.awvalid && m.wvalid;
    s.wready  = s.awready;
    s.rvalid  = (tila == VASTAUS) && !kirjoitus;
    s.bvalid  = (tila == VASTAUS) && kirjoitus;
    s.rdata   = ldata;
    s.rresp   = vastaus;
    s.bresp   = vastaus;
  end

  apb_s2m_t valittu_s;
  assign valittu_s = laite_ok ? apb_s[laite[2:0]] : '0;

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila      <= VAPAA;
      kirjoitus <= 1'b0;
      osoite    <= '0;
      kdata     <= '0;
      tavut     <= '0;
      ldata     <= '0;
      vastaus   <= OKAY;
    end else begin
      case (tila)
        VAPAA:
          if (s.awready) begin
            kirjoitus <= 1'b1;
            osoite    <= m.awaddr[15:0];
            kdata     <= m.wdata;
            tavut     <= m.wstrb;
            tila      <= SETUP;
          end else if (m.arvalid) begin
            kirjoitus <= 1'b0;
            osoite    <= m.araddr[15:0];
            tila      <= SETUP;
          end
        SETUP:
          if (laite_ok) tila <= ACCESS;
          else begin
            vastaus <= DECERR;          // tyhjä ikkuna
            ldata   <= '0;
            tila    <= VASTAUS;
          end
        ACCESS:
          if (valittu_s.pready) begin
            vastaus <= valittu_s.pslverr ? SLVERR : OKAY;
            ldata   <= valittu_s.prdata;
            tila    <= VASTAUS;
          end
        VASTAUS:
          if ((s.rvalid && m.rready) || (s.bvalid && m.bready))
            tila <= VAPAA;
        default: tila <= VAPAA;
      endcase
    end
  end

endmodule
