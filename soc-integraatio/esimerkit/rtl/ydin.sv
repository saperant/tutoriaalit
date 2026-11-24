// Ydin: monivaiheinen RV32I-suoritin, jossa on Zicsr ja M-tilan ansat.
//
// Tarkoitus on opetuksellinen: jokainen käsky kulkee vaiheet HAE →
// SUORITA (→ MUISTI) ilman liukuhihnaa, joten väyläliikenne on helppo
// seurata. Ydin käyttää yksinkertaista pyyntö/valmis-väylää; silta.sv
// muuntaa sen AXI4-Liteksi.
//
// Toteutetut CSR:t: mstatus (MIE, MPIE), misa, mie, mtvec, mscratch,
// mepc, mcause, mtval, mip (vain luku), mcycle/cycle ja mhartid.
// Ansat: käskyn ja datan väylävirhe, kohdistusvirhe, laiton käsky,
// ecall, ebreak sekä ajastin- ja ulkoinen keskeytys.
module ydin (
  input  logic        kello,
  input  logic        nollaus_n,
  // @alku vayla
  // Ytimen väylä: pyyntö pysyy ylhäällä, kunnes valmis nousee.
  output logic        v_pyynto,
  output logic        v_kirjoita,
  output logic [31:0] v_osoite,
  output logic [31:0] v_kdata,
  output logic [3:0]  v_tavut,
  input  logic        v_valmis,
  input  logic [31:0] v_ldata,
  input  logic        v_virhe,
  // @loppu vayla
  input  logic        ajastin_kesk,   // MTIP CLINTiltä
  input  logic        ulkoinen_kesk   // MEIP keskeytysohjaimelta
);

  typedef enum logic [1:0] {HAE, SUORITA, MUISTI} tila_t;
  tila_t tila;

  logic [31:0] pc, ir;
  logic [31:0] x [32];

  // CSR-tila.
  logic        mie_bit, mpie;       // mstatus.MIE ja mstatus.MPIE
  logic        mtie, meie;          // mie.MTIE ja mie.MEIE
  logic [31:0] mtvec, mscratch, mepc, mcause, mtval;
  logic [63:0] mcycle;

  // Käskyn kentät.
  logic [6:0]  opc;
  logic [2:0]  f3;
  logic [6:0]  f7;
  logic [4:0]  rd, rs1, rs2;
  logic [31:0] a, b;
  logic [31:0] imm_i, imm_s, imm_b, imm_u, imm_j;

  assign opc = ir[6:0];
  assign rd  = ir[11:7];
  assign f3  = ir[14:12];
  assign rs1 = ir[19:15];
  assign rs2 = ir[24:20];
  assign f7  = ir[31:25];
  assign a   = (rs1 == 5'd0) ? 32'd0 : x[rs1];
  assign b   = (rs2 == 5'd0) ? 32'd0 : x[rs2];
  assign imm_i = {{20{ir[31]}}, ir[31:20]};
  assign imm_s = {{20{ir[31]}}, ir[31:25], ir[11:7]};
  assign imm_b = {{19{ir[31]}}, ir[31], ir[7], ir[30:25], ir[11:8],
                  1'b0};
  assign imm_u = {ir[31:12], 12'd0};
  assign imm_j = {{11{ir[31]}}, ir[31], ir[19:12], ir[20], ir[30:21],
                  1'b0};

  // ALU: OP ja OP-IMM. Bitti 30 erottaa SUB/ADD ja SRA/SRL.
  function automatic logic [31:0] alu(input logic [2:0] f,
                                      input logic alt,
                                      input logic [31:0] p,
                                      input logic [31:0] q);
    case (f)
      3'b000:  return alt ? p - q : p + q;
      3'b001:  return p << q[4:0];
      3'b010:  return {31'd0, $signed(p) < $signed(q)};
      3'b011:  return {31'd0, p < q};
      3'b100:  return p ^ q;
      3'b101:  return alt ? 32'($signed(p) >>> q[4:0]) : p >> q[4:0];
      3'b110:  return p | q;
      default: return p & q;
    endcase
  endfunction

  function automatic logic ehto(input logic [2:0] f,
                                input logic [31:0] p,
                                input logic [31:0] q);
    case (f)
      3'b000:  return p == q;
      3'b001:  return p != q;
      3'b100:  return $signed(p) < $signed(q);
      3'b101:  return $signed(p) >= $signed(q);
      3'b110:  return p < q;
      default: return p >= q;           // 3'b111 (BGEU)
    endcase
  endfunction

  // Muistikäskyn osoite ja kohdistus.
  logic [31:0] m_osoite;
  logic        m_kohdistettu;
  assign m_osoite = a + ((opc == 7'b0100011) ? imm_s : imm_i);
  always_comb begin
    case (f3[1:0])
      2'b00:   m_kohdistettu = 1'b1;
      2'b01:   m_kohdistettu = ~m_osoite[0];
      default: m_kohdistettu = (m_osoite[1:0] == 2'b00);
    endcase
  end

  // Ladatun arvon sovitus: siirto ja etumerkin laajennus.
  /* verilator lint_off UNUSEDSIGNAL */
  logic [31:0] lsiirto;           // tavu- ja puolisanaluvut käyttävät osan
  /* verilator lint_on UNUSEDSIGNAL */
  logic [31:0] ladattu;
  assign lsiirto = v_ldata >> {v_osoite[1:0], 3'b000};
  always_comb begin
    case (f3)
      3'b000:  ladattu = {{24{lsiirto[7]}}, lsiirto[7:0]};
      3'b001:  ladattu = {{16{lsiirto[15]}}, lsiirto[15:0]};
      3'b100:  ladattu = {24'd0, lsiirto[7:0]};
      3'b101:  ladattu = {16'd0, lsiirto[15:0]};
      default: ladattu = v_ldata;
    endcase
  end

  // CSR:n luku. tuntematon_csr ilmaisee laittoman käskyn.
  logic [11:0] csr_nro;
  logic [31:0] csr_arvo;
  logic        tuntematon_csr;
  assign csr_nro = ir[31:20];
  always_comb begin
    tuntematon_csr = 1'b0;
    case (csr_nro)
      12'h300: csr_arvo = {24'd0, mpie, 3'd0, mie_bit, 3'd0};
      12'h301: csr_arvo = 32'h4000_0100;           // RV32I
      12'h304: csr_arvo = {20'd0, meie, 3'd0, mtie, 7'd0};
      12'h305: csr_arvo = mtvec;
      12'h340: csr_arvo = mscratch;
      12'h341: csr_arvo = mepc;
      12'h342: csr_arvo = mcause;
      12'h343: csr_arvo = mtval;
      12'h344: csr_arvo = {20'd0, ulkoinen_kesk, 3'd0, ajastin_kesk,
                           7'd0};
      12'hB00, 12'hC00: csr_arvo = mcycle[31:0];
      12'hB80, 12'hC80: csr_arvo = mcycle[63:32];
      12'hF14: csr_arvo = 32'd0;                   // mhartid
      default: begin csr_arvo = 32'd0; tuntematon_csr = 1'b1; end
    endcase
  end

  // CSR:n uusi arvo: CSRRW/CSRRS/CSRRC ja niiden välittömät muodot.
  logic [31:0] csr_lahde, csr_uusi;
  assign csr_lahde = f3[2] ? {27'd0, rs1} : a;
  always_comb begin
    case (f3[1:0])
      2'b01:   csr_uusi = csr_lahde;
      2'b10:   csr_uusi = csr_arvo | csr_lahde;
      default: csr_uusi = csr_arvo & ~csr_lahde;
    endcase
  end

  // @alku keskeytys
  // Odottava keskeytys tarkistetaan ennen jokaista hakua. Ulkoinen
  // keskeytys (MEI) on etusijalla ajastimeen (MTI) nähden. Kesken olevaa
  // hakua ei keskeytetä: väyläpyyntöä ei saa perua ennen vastausta.
  logic haku_kesken, kesk_ulk, kesk_ajastin;
  assign kesk_ulk     = !haku_kesken && mie_bit && meie && ulkoinen_kesk;
  assign kesk_ajastin = !haku_kesken && mie_bit && mtie && ajastin_kesk;
  // @loppu keskeytys

  // Väyläpyyntö: haku tai muistikäsky.
  always_comb begin
    v_pyynto   = 1'b0;
    v_kirjoita = 1'b0;
    v_osoite   = pc;
    v_kdata    = 32'd0;
    v_tavut    = 4'b0000;
    if (tila == HAE && !kesk_ulk && !kesk_ajastin) begin
      v_pyynto = 1'b1;
    end else if (tila == MUISTI) begin
      v_pyynto   = 1'b1;
      v_kirjoita = (opc == 7'b0100011);
      v_osoite   = m_osoite;
      case (f3[1:0])
        2'b00:   begin v_kdata = {4{b[7:0]}};
                       v_tavut = 4'b0001 << m_osoite[1:0]; end
        2'b01:   begin v_kdata = {2{b[15:0]}};
                       v_tavut = 4'b0011 << m_osoite[1:0]; end
        default: begin v_kdata = b; v_tavut = 4'b1111; end
      endcase
    end
  end

  // @alku ansa
  // Ansaan siirtyminen: tallenna syy ja paluuosoite, estä keskeytykset.
  task automatic ansa(input logic [31:0] syy, input logic [31:0] arvo,
                      input logic [31:0] paluu);
    mcause  <= syy;
    mtval   <= arvo;
    mepc    <= paluu;
    mpie    <= mie_bit;
    mie_bit <= 1'b0;
    pc      <= {mtvec[31:2], 2'b00};
    tila    <= HAE;
  endtask
  // @loppu ansa

  task automatic kirjoita_rd(input logic [31:0] arvo);
    if (rd != 5'd0) x[rd] <= arvo;
  endtask

  always_ff @(posedge kello or negedge nollaus_n) begin
    if (!nollaus_n) begin
      tila     <= HAE;
      pc       <= 32'd0;
      ir       <= 32'd0;
      mie_bit  <= 1'b0;
      mpie     <= 1'b0;
      mtie     <= 1'b0;
      meie     <= 1'b0;
      mtvec    <= 32'd0;
      mscratch <= 32'd0;
      mepc     <= 32'd0;
      mcause   <= 32'd0;
      mtval    <= 32'd0;
      mcycle   <= 64'd0;
      haku_kesken <= 1'b0;
    end else begin
      mcycle <= mcycle + 64'd1;
      if (tila == HAE)
        haku_kesken <= v_pyynto && !v_valmis;
      case (tila)
        HAE: begin
          if (kesk_ulk)
            ansa(32'h8000_000B, 32'd0, pc);
          else if (kesk_ajastin)
            ansa(32'h8000_0007, 32'd0, pc);
          else if (v_valmis) begin
            if (v_virhe) ansa(32'd1, pc, pc);  // käskyn väylävirhe
            else begin
              ir   <= v_ldata;
              tila <= SUORITA;
            end
          end
        end
        SUORITA: begin
          tila <= HAE;
          pc   <= pc + 32'd4;
          case (opc)
            7'b0110111: kirjoita_rd(imm_u);                 // LUI
            7'b0010111: kirjoita_rd(pc + imm_u);            // AUIPC
            7'b1101111: begin                               // JAL
              kirjoita_rd(pc + 32'd4);
              pc <= pc + imm_j;
            end
            7'b1100111: begin                               // JALR
              kirjoita_rd(pc + 32'd4);
              pc <= (a + imm_i) & ~32'd1;
            end
            7'b1100011:                                     // haarat
              if (ehto(f3, a, b)) pc <= pc + imm_b;
            7'b0000011, 7'b0100011: begin                   // LOAD/STORE
              pc <= pc;
              if (!m_kohdistettu)
                ansa(opc[5] ? 32'd6 : 32'd4, m_osoite, pc);
              else
                tila <= MUISTI;
            end
            7'b0010011:                                     // OP-IMM
              kirjoita_rd(alu(f3, f3 == 3'b101 && ir[30], a, imm_i));
            7'b0110011:                                     // OP
              if (f7 == 7'd0 || f7 == 7'b0100000)
                kirjoita_rd(alu(f3, ir[30], a, b));
              else ansa(32'd2, ir, pc);
            7'b0001111: ;                                   // FENCE
            7'b1110011: begin                               // SYSTEM
              if (f3 == 3'b000) begin
                case (ir[31:20])
                  12'h000: ansa(32'd11, 32'd0, pc);         // ECALL
                  12'h001: ansa(32'd3, pc, pc);             // EBREAK
                  12'h302: begin                            // MRET
                    pc      <= mepc;
                    mie_bit <= mpie;
                    mpie    <= 1'b1;
                  end
                  12'h105: ;                                // WFI
                  default: ansa(32'd2, ir, pc);
                endcase
              end else if (tuntematon_csr || f3 == 3'b100) begin
                ansa(32'd2, ir, pc);
              end else begin
                kirjoita_rd(csr_arvo);
                // CSRRS/CSRRC lähteellä x0 eivät kirjoita CSR:ään.
                if (f3[1:0] == 2'b01 || rs1 != 5'd0) begin
                  case (csr_nro)
                    12'h300: begin
                      mie_bit <= csr_uusi[3];
                      mpie    <= csr_uusi[7];
                    end
                    12'h304: begin
                      mtie <= csr_uusi[7];
                      meie <= csr_uusi[11];
                    end
                    12'h305: mtvec    <= csr_uusi;
                    12'h340: mscratch <= csr_uusi;
                    12'h341: mepc     <= {csr_uusi[31:2], 2'b00};
                    12'h342: mcause   <= csr_uusi;
                    12'h343: mtval    <= csr_uusi;
                    default: ;     // vain luku: kirjoitus ohitetaan
                  endcase
                end
              end
            end
            default: ansa(32'd2, ir, pc);                   // laiton
          endcase
        end
        MUISTI: begin
          if (v_valmis) begin
            if (v_virhe)
              ansa(opc[5] ? 32'd7 : 32'd5, m_osoite, pc);
            else begin
              if (!opc[5]) kirjoita_rd(ladattu);
              pc   <= pc + 32'd4;
              tila <= HAE;
            end
          end
        end
        default: tila <= HAE;
      endcase
    end
  end

endmodule
