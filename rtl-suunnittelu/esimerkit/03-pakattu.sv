module testipenkki;
  // @alku tyypit
  typedef enum logic [3:0] {
    LAMPOTILA = 4'h1,
    KOSTEUS   = 4'h2,
    PAINE     = 4'h3
  } suure_t;

  // Pakattu rakenne on bittivektori, jolla on nimetyt kentät.
  // Ensimmäinen kenttä on merkitsevin.
  typedef struct packed {
    suure_t            suure;    // [23:20]
    logic [7:0]        anturi;   // [19:12]
    logic signed [11:0] arvo;    // [11:0], kahden komplementti
  } mittaus_t;
  // @loppu tyypit

  // @alku kaytto
  mittaus_t   m;
  logic [23:0] vayla;

  initial begin
    m = '{suure: LAMPOTILA, anturi: 8'd42, arvo: -12'sd215};
    vayla = m;                       // rakenne on suoraan 24 bittiä
    $display("väylällä: %h", vayla);

    m = mittaus_t'(24'h3_07_0FF);    // ja takaisin
    $display("suure %s, anturi %0d, arvo %0d",
             m.suure.name(), m.anturi, m.arvo);
  end
  // @loppu kaytto

  // @alku operaattorit
  logic [7:0] tavu;
  initial begin
    #1 tavu = 8'b1011_0010;
    $display("pariteetti ^tavu = %b", ^tavu);
    $display("kaikki ykkösiä &tavu = %b, yksikin |tavu = %b",
             &tavu, |tavu);
    $display("liitos {4'hA, tavu[3:0]} = %h", {4'hA, tavu[3:0]});
    $display("toisto {4{2'b10}} = %b", {4{2'b10}});
    $display("etumerkkilaajennus {{8{tavu[7]}}, tavu} = %h",
             {{8{tavu[7]}}, tavu});
  end
  // @loppu operaattorit
endmodule
