// @alku liitanta
// Numeerisesti ohjattu oskillaattori: vaiheakkumulaattori ja
// neljännesjakson sinitaulukko lohko-RAMissa. Taajuus on
// taajuussana / 2**PW näytetaajuudesta. Vaiheesta käytetään AW + 2
// ylintä bittiä; loput katkaistaan. Ulostulo Q1.11, latenssi neljä
// jaksoa. Vastapaine pysäyttää myös vaiheen.
module nco #(
  parameter int PW = 24,                     // vaiheakkumulaattori
  parameter int AW = 8,                      // taulukon osoite
  parameter int OW = 12,                     // ulostulo
  parameter     TAULUKKO = "rtl/nco_sini.hex"
) (
  input  logic                 clk,
  input  logic                 nollaus,
  input  logic [PW-1:0]        taajuussana,
  output logic                 m_valid,
  input  logic                 m_ready,
  output logic signed [OW-1:0] m_data
);
  // @loppu liitanta
  logic eteen;
  assign eteen = !m_valid || m_ready;

  // @alku taulukko
  // Neljännesjakso, 2**AW riviä, arvot 0..2**(OW-1)-1 etumerkittä.
  logic [OW-2:0] rom [2**AW];
  initial $readmemh(TAULUKKO, rom);
  // @loppu taulukko

  // @alku liukuhihna
  logic [PW-1:0]   akku;
  logic [AW+1:0]   vaihe;                    // neljännes ja osoite
  logic [AW-1:0]   osoite;
  logic [OW-2:0]   arvo;
  logic            neg2, neg3;
  logic [3:0]      v;

  always_ff @(posedge clk)
    if (nollaus) begin
      akku <= '0;
      v    <= '0;
    end else if (eteen) begin
      akku   <= akku + taajuussana;           // 1: vaihe
      vaihe  <= akku[PW-1 -: AW+2];           //    katkaisu
      // 2: neljänneksen peilaus kääntää osoitteen bitit
      osoite <= vaihe[AW] ? ~vaihe[AW-1:0] : vaihe[AW-1:0];
      neg2   <= vaihe[AW+1];
      arvo   <= rom[osoite];                  // 3: lohko-RAM
      neg3   <= neg2;
      m_data <= neg3 ? -$signed({1'b0, arvo}) // 4: etumerkki
                     :  $signed({1'b0, arvo});
      v      <= {v[2:0], 1'b1};
    end

  assign m_valid = v[3];
  // @loppu liukuhihna
endmodule
