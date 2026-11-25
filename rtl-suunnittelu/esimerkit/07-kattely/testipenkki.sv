// Tuottaja -> skid-puskuri -> kättelyvaihe -> kuluttaja. Tuottaja pitää
// taukoja ja kuluttaja pysäyttää virran näennäissatunnaisesti; jokaisen
// sanan on tultava perille kerran ja oikeassa järjestyksessä.
module testipenkki;
  localparam int SANOJA = 200;

  logic        clk = 1'b0, rst_n = 1'b0, kaynnissa = 1'b1;
  logic        s_kelv = 1'b0, s_valmis;
  logic [7:0]  s_data = '0;
  logic        m_kelv, m_valmis;
  logic [7:0]  m_data;
  logic        u_kelv, u_valmis = 1'b0;
  logic [7:0]  u_data;
  logic [15:0] arpa = 16'hACE1;
  logic        siirtyi = 1'b0;
  int          lahetetty = 0, perilla = 0;
  int          pysaytyksia = 0, varalla = 0;

  skid_puskuri u_skid (
    .clk, .rst_n, .s_kelv, .s_valmis, .s_data,
    .u_kelv(m_kelv), .u_valmis(m_valmis), .u_data(m_data));
  kattelyvaihe u_vaihe (
    .clk, .rst_n, .s_kelv(m_kelv), .s_valmis(m_valmis), .s_data(m_data),
    .u_kelv, .u_valmis, .u_data);

  initial while (kaynnissa) #5 clk = ~clk;

  // @alku tarkistin
  // Sana siirtyy reunalla, jolla sekä kelvollinen että valmis ovat 1.
  always @(posedge clk) begin
    if (u_kelv && u_valmis) begin
      if (u_data != 8'(perilla))
        $fatal(1, "odotettiin %0d, saatiin %0d", perilla, u_data);
      perilla <= perilla + 1;
    end
    if (u_kelv && !u_valmis) pysaytyksia <= pysaytyksia + 1;
    if (u_skid.vara_kelv)    varalla     <= varalla + 1;
  end
  // @loppu tarkistin

  initial begin
    #12 rst_n = 1'b1;
    @(posedge clk); #1;
    while (perilla < SANOJA) begin
      arpa = {arpa[14:0], arpa[15] ^ arpa[13] ^ arpa[12] ^ arpa[10]};
      // @alku tuottaja
      // Tuottaja noudattaa kättelyn sääntöä: nostettu s_kelv ja data
      // pysyvät, kunnes siirto on tapahtunut.
      if (!s_kelv || siirtyi) begin
        if (lahetetty < SANOJA && arpa[1:0] != 2'b00) begin
          s_kelv    = 1'b1;
          s_data    = 8'(lahetetty);
          lahetetty = lahetetty + 1;
        end else begin
          s_kelv = 1'b0;
        end
      end
      // Kuluttaja on valmis noin kahdella jaksolla kolmesta.
      u_valmis = (arpa[7:6] != 2'b11) && (arpa[4:2] != 3'b000);
      @(negedge clk);
      siirtyi = s_kelv && s_valmis;      // toteutuu tulevalla reunalla
      // @loppu tuottaja
      @(posedge clk); #1;
    end
    $display("%0d sanaa perillä järjestyksessä", perilla);
    $display("kuluttaja pysäytti virran %0d jaksolla", pysaytyksia);
    $display("varapaikka käytössä %0d jaksolla", varalla);
    if (pysaytyksia == 0 || varalla == 0)
      $fatal(1, "vastapaine jäi testaamatta");
    kaynnissa = 1'b0;
  end
endmodule
