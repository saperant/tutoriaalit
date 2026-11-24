// Väylien tyypit: AXI4-Lite ja APB pakattuina rakenteina.
//
// Rakenne kokoaa yhden suunnan signaalit, joten moduulien portit pysyvät
// lyhyinä ja kytkimeen voidaan tehdä taulukoita. Kenttien nimet ovat
// AMBA-määrittelyn nimet ilman A-, W-, B-, R-etuliitteen isoa kirjainta.
package vaylat;

  // @alku axil
  // AXI4-Lite: isäntä → orja (master → slave).
  typedef struct packed {
    logic [31:0] awaddr;   // kirjoitusosoite
    logic        awvalid;
    logic [31:0] wdata;    // kirjoitusdata
    logic [3:0]  wstrb;    // tavukohtaiset kirjoitusluvat
    logic        wvalid;
    logic        bready;   // isäntä valmis vastaanottamaan vastauksen
    logic [31:0] araddr;   // lukuosoite
    logic        arvalid;
    logic        rready;
  } axil_m2s_t;

  // AXI4-Lite: orja → isäntä.
  typedef struct packed {
    logic        awready;
    logic        wready;
    logic [1:0]  bresp;    // kirjoituksen vastaus
    logic        bvalid;
    logic        arready;
    logic [31:0] rdata;
    logic [1:0]  rresp;    // lukemisen vastaus
    logic        rvalid;
  } axil_s2m_t;

  // Vastauskoodit (xRESP).
  /* verilator lint_off UNUSEDPARAM */
  localparam logic [1:0] OKAY   = 2'b00;
  localparam logic [1:0] SLVERR = 2'b10;  // orja tunnisti virheen
  localparam logic [1:0] DECERR = 2'b11;  // osoitteessa ei ole orjaa
  /* verilator lint_on UNUSEDPARAM */
  // @loppu axil

  // @alku apb
  // APB (AMBA 3/4): isäntä (silta) → orja. Jokaisella orjalla on oma
  // PSEL; muut signaalit ovat yhteisiä.
  typedef struct packed {
    logic [11:0] paddr;    // osoite orjan 4 KiB:n ikkunassa
    logic        psel;
    logic        penable;  // siirron toinen (ACCESS-)vaihe
    logic        pwrite;
    logic [31:0] pwdata;
    logic [3:0]  pstrb;
  } apb_m2s_t;

  typedef struct packed {
    logic [31:0] prdata;
    logic        pready;   // orja on valmis: siirto päättyy
    logic        pslverr;  // orja tunnisti virheen
  } apb_s2m_t;
  // @loppu apb

endpackage
