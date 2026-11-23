// UART-lähetin: 8 databittiä, ei pariteettia, 1 lopetusbitti (8N1).
// Kättely: tavu siirtyy, kun kelvollinen && valmis samalla reunalla.
module uart_tx #(
  parameter int KELLO_HZ = 50_000_000,
  parameter int BAUD     = 115_200
) (
  input  logic       clk,
  input  logic       rst_n,
  input  logic [7:0] data,
  input  logic       kelvollinen,
  output logic       valmis,
  output logic       tx               // lepotila 1
);
  localparam int JAKSO = KELLO_HZ / BAUD;  // kellojaksoa bittiä kohden
  localparam int LW    = $clog2(JAKSO);

  // @alku tilat
  typedef enum logic [1:0] {LEPO, ALKU, DATA, LOPPU} tila_t;
  tila_t        tila_q, tila_d;
  logic [LW-1:0] jakso_q, jakso_d;    // jakson sisäinen laskuri
  logic [2:0]   bitti_q, bitti_d;     // monesko databitti
  logic [7:0]   siirto_q, siirto_d;   // lähtevä tavu
  logic         tx_d;
  // @loppu tilat

  logic bitti_ohi;
  assign bitti_ohi = (jakso_q == LW'(JAKSO - 1));

  // @alku seuraava
  always_comb begin
    // Oletukset: pysy tilassa, laske jaksoa, linja lepotilaan.
    tila_d   = tila_q;
    jakso_d  = bitti_ohi ? '0 : jakso_q + 1'b1;
    bitti_d  = bitti_q;
    siirto_d = siirto_q;
    tx_d     = 1'b1;
    valmis   = 1'b0;

    unique case (tila_q)
      LEPO: begin
        valmis  = 1'b1;
        jakso_d = '0;
        if (kelvollinen) begin
          siirto_d = data;
          tila_d   = ALKU;
        end
      end
      ALKU: begin
        tx_d = 1'b0;                      // aloitusbitti
        if (bitti_ohi) begin
          bitti_d = '0;
          tila_d  = DATA;
        end
      end
      DATA: begin
        tx_d = siirto_q[0];               // vähiten merkitsevä ensin
        if (bitti_ohi) begin
          siirto_d = siirto_q >> 1;
          bitti_d  = bitti_q + 1'b1;
          if (bitti_q == 3'd7) tila_d = LOPPU;
        end
      end
      LOPPU: begin
        if (bitti_ohi) tila_d = LEPO;     // tx_d = 1: lopetusbitti
      end
    endcase
  end
  // @loppu seuraava

  // @alku rekisterit
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      tila_q   <= LEPO;
      jakso_q  <= '0;
      bitti_q  <= '0;
      siirto_q <= '0;
      tx       <= 1'b1;                   // linja lepää ykkösenä
    end else begin
      tila_q   <= tila_d;
      jakso_q  <= jakso_d;
      bitti_q  <= bitti_d;
      siirto_q <= siirto_d;
      tx       <= tx_d;                   // rekisteröity: ei piikkejä
    end
  end
  // @loppu rekisterit
endmodule
