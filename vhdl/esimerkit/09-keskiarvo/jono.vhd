-- @alku jono
-- Testipenkkien jono odotetuille arvoille. Suojattu tyyppi (protected)
-- on VHDL:n tapa jakaa tilaa prosessien välillä: sen metodit
-- suoritetaan yksi kerrallaan, joten tila ei voi korruptoitua.
package jono_pkg is
  type jono_t is protected
    procedure lisaa(arvo : integer);
    impure function ota return integer;
    impure function koko return natural;
  end protected jono_t;
end package jono_pkg;

package body jono_pkg is
  type jono_t is protected body
    constant TILA : positive := 1024;
    type taulu_t is array (0 to TILA - 1) of integer;
    variable taulu       : taulu_t;
    variable alku, maara : natural := 0;

    procedure lisaa(arvo : integer) is
    begin
      assert maara < TILA report "jono täynnä" severity failure;
      taulu((alku + maara) mod TILA) := arvo;
      maara := maara + 1;
    end procedure lisaa;

    impure function ota return integer is
      variable arvo : integer;
    begin
      assert maara > 0 report "jono tyhjä" severity failure;
      arvo  := taulu(alku);
      alku  := (alku + 1) mod TILA;
      maara := maara - 1;
      return arvo;
    end function ota;

    impure function koko return natural is
    begin
      return maara;
    end function koko;
  end protected body jono_t;
end package body jono_pkg;
-- @loppu jono
