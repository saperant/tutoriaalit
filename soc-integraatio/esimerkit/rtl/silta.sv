// Silta: ytimen pyyntö/valmis-väylä → AXI4-Lite-isäntä.
//
// Yksi siirto kerrallaan. Kirjoituksessa AW- ja W-kanava esitetään
// yhtä aikaa ja kumpikin pidetään ylhäällä omaan kättelyynsä asti.
module silta
  import vaylat::*;
(
  input  logic        kello,
  input  logic        nollaus_n,
  input  logic        v_pyynto,
  input  logic        v_kirjoita,
  input  logic [31:0] v_osoite,
  input  logic [31:0] v_kdata,
  input  logic [3:0]  v_tavut,
  output logic        v_valmis,
  output logic [31:0] v_ldata,
  output logic        v_virhe,
  output axil_m2s_t   m,
  input  axil_s2m_t   s
);

  typedef enum logic [1:0] {VAPAA, LUKU, KIRJOITUS} tila_t;
  tila_t tila;
  logic  osoite_tehty, w_tehty;  // AR- tai AW-kättely ja W-kättely

  // @alku kanavat
  always_comb begin
    m = '0;
    m.araddr  = v_osoite;
    m.awaddr  = v_osoite;
    m.wdata   = v_kdata;
    m.wstrb   = v_tavut;
    m.arvalid = (tila == LUKU) && !osoite_tehty;
    m.rready  = (tila == LUKU);
    m.awvalid = (tila == KIRJOITUS) && !osoite_tehty;
    m.wvalid  = (tila == KIRJOITUS) && !w_tehty;
    m.bready  = (tila == KIRJOITUS);
  end

  assign v_valmis = (tila == LUKU && s.rvalid) ||
                    (tila == KIRJOITUS && s.bvalid);
  assign v_ldata  = s.rdata;
  assign v_virhe  = (tila == LUKU) ? s.rresp[1] : s.bresp[1];
  // @loppu kanavat

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila     <= VAPAA;
      osoite_tehty <= 1'b0;
      w_tehty  <= 1'b0;
    end else begin
      case (tila)
        VAPAA: if (v_pyynto) tila <= v_kirjoita ? KIRJOITUS : LUKU;
        LUKU: begin
          if (m.arvalid && s.arready) osoite_tehty <= 1'b1;
          if (s.rvalid) begin
            tila     <= VAPAA;
            osoite_tehty <= 1'b0;
          end
        end
        KIRJOITUS: begin
          if (m.awvalid && s.awready) osoite_tehty <= 1'b1;
          if (m.wvalid && s.wready)   w_tehty  <= 1'b1;
          if (s.bvalid) begin
            tila     <= VAPAA;
            osoite_tehty <= 1'b0;
            w_tehty  <= 1'b0;
          end
        end
        default: tila <= VAPAA;
      endcase
    end
  end

endmodule
