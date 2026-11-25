// @alku liitanta
// Kortin esittelysuunnitelma. Kaikki logiikka toimii pikselikellolla.
//   ledit 1-4   juokseva valo, askel ASKEL kehyksen välein
//   ledi 5      painikkeen 1 suodatettu tila
//   painike 1   kasvattaa laskuria; luku näkyy kuvassa ja sarjaportissa
//   painike 2   kääntää juoksevan valon suunnan
//   painike 3   pysäyttää pallon niin kauan kuin se on pohjassa
//   sarjaportti merkit '0'-'7' valitsevat pallon värin
module demo #(
  parameter int KELLOT_PER_BITTI = 218,    // 25,125 MHz / 115200
  parameter int SUODIN = 17,               // painikkeen suodatus, 2**17
  parameter int ASKEL = 3
) (
  input  logic        clk,
  input  logic        nollaus,
  input  logic [3:1]  painike,
  input  logic        rx,
  output logic        tx,
  output logic [5:1]  led,
  output logic        hsync_n,
  output logic        vsync_n,
  output logic [11:0] rgb
);
// @loppu liitanta
  // Painikkeet. Kaikkia lähtöjä ei käytetä: painike 2 antaa vain
  // pulssin ja painike 3 vain tilan.
  /* verilator lint_off UNUSEDSIGNAL */
  logic [3:1] tila, painettu;
  /* verilator lint_on UNUSEDSIGNAL */
  for (genvar i = 1; i <= 3; i++) begin : g_painike
    painike #(.LEVEYS(SUODIN)) suodin (
      .clk, .nollaus, .tulo(painike[i]),
      .tila(tila[i]), .painettu(painettu[i]));
  end

  // Näyttö.
  logic [9:0]  x, y, px, py;
  logic        nakyva, hs, vs, kehys;
  logic [11:0] vari_nyt;
  logic [2:0]  vari = 3'b001;
  logic [7:0]  luku = '0;

  vga_ajoitus ajoitus (
    .clk, .nollaus, .x, .y, .nakyva,
    .hsync_n(hs), .vsync_n(vs), .kehys);
  pallo liike (
    .clk, .nollaus, .kehys, .pysayta(tila[3]), .px, .py);
  kuva sisalto (.x, .y, .px, .py, .vari, .luku, .rgb(vari_nyt));

// @alku lahto
  // Värit ja tahdistus rekisteröidään samalla reunalla, jotta ne
  // pysyvät kohdakkain. Kuva-alueen ulkopuolella värin on oltava musta.
  initial begin hsync_n = 1'b1; vsync_n = 1'b1; rgb = '0; end
  always_ff @(posedge clk) begin
    hsync_n <= hs;
    vsync_n <= vs;
    rgb     <= nakyva ? vari_nyt : '0;
  end
// @loppu lahto

  // Juokseva valo.
  logic [3:0] valo = 4'b0001;
  logic       vasemmalle = 1'b1;
  logic [3:0] kehyksia = '0;
  always_ff @(posedge clk)
    if (nollaus) begin
      valo       <= 4'b0001;
      vasemmalle <= 1'b1;
      kehyksia   <= '0;
    end else begin
      if (painettu[2]) vasemmalle <= !vasemmalle;
      if (kehys) begin
        if (kehyksia == 4'(ASKEL - 1)) begin
          kehyksia <= '0;
          valo <= vasemmalle ? {valo[2:0], valo[3]} : {valo[0], valo[3:1]};
        end else begin
          kehyksia <= kehyksia + 1'b1;
        end
      end
    end
  assign led = {tila[1], valo};

  // Sarjaportti.
  logic       rx_kelpaa, tx_laheta = 1'b0, tx_valmis;
  logic [7:0] rx_tavu, tx_tavu = '0;
  uart_rx #(.KELLOT_PER_BITTI(KELLOT_PER_BITTI)) vastaanotin (
    .clk, .rx, .kelpaa(rx_kelpaa), .tavu(rx_tavu));
  uart_tx #(.KELLOT_PER_BITTI(KELLOT_PER_BITTI)) lahetin (
    .clk, .laheta(tx_laheta), .tavu(tx_tavu), .valmis(tx_valmis), .tx);

  function automatic logic [7:0] heksa(input logic [3:0] n);
    heksa = n < 4'd10 ? 8'd48 + 8'(n) : 8'd55 + 8'(n);   // '0' tai 'A'
  endfunction

// @alku viestit
  // Lähtevä viesti on enintään viisi merkkiä siirtorekisterissä.
  // Painallus lähettää "N=xx" ja rivinvaihdon; vastaanotettu merkki
  // kuitataan merkillä itsellään tai kysymysmerkillä.
  logic [39:0] viesti = '0;
  logic [2:0]  jaljella = '0;
  logic [7:0]  seuraava;
  assign seuraava = luku + 1'b1;

  always_ff @(posedge clk) begin
    tx_laheta <= 1'b0;
    if (nollaus) begin
      luku     <= '0;
      vari     <= 3'b001;
      jaljella <= '0;
    end else if (painettu[1]) begin
      luku     <= seuraava;
      viesti   <= {"N", "=", heksa(seuraava[7:4]), heksa(seuraava[3:0]),
                   8'h0a};
      jaljella <= 3'd5;
    end else if (rx_kelpaa) begin
      if (rx_tavu[7:3] == 5'b00110) vari <= rx_tavu[2:0];   // '0'-'7'
      viesti   <= {rx_tavu[7:3] == 5'b00110 ? rx_tavu : 8'h3f, 8'h0a,
                   24'd0};
      jaljella <= 3'd2;
    end else if (jaljella != 0 && tx_valmis && !tx_laheta) begin
      tx_tavu   <= viesti[39:32];
      tx_laheta <= 1'b1;
      viesti    <= {viesti[31:0], 8'd0};
      jaljella  <= jaljella - 1'b1;
    end
  end
// @loppu viestit
endmodule
