-- @alku paketti
package alu_pkg is
  type operaatio_t is (SUMMA, EROTUS, JA, TAI, XTAI, SIIRTO_V, SIIRTO_O,
                       PIENEMPI);
end package alu_pkg;
-- @loppu paketti

-- @alku alu
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.alu_pkg.all;

-- 8-bittinen ALU. Kanto on erotuksessa lainaus, siirroissa ulos
-- siirtynyt bitti. PIENEMPI vertaa etumerkillisinä lukuina.
entity alu is
  port (
    op    : in  operaatio_t;
    a, b  : in  std_logic_vector(7 downto 0);
    tulos : out std_logic_vector(7 downto 0);
    kanto : out std_logic;
    nolla : out std_logic
  );
end entity alu;

architecture rtl of alu is
  signal t : std_logic_vector(7 downto 0);
begin
  laskenta : process (all)
    variable ua, ub : unsigned(8 downto 0);
    variable laaja  : unsigned(8 downto 0);
  begin
    ua := resize(unsigned(a), 9);
    ub := resize(unsigned(b), 9);
    kanto <= '0';
    case op is
      when SUMMA =>
        laaja := ua + ub;
        t     <= std_logic_vector(laaja(7 downto 0));
        kanto <= laaja(8);
      when EROTUS =>
        laaja := ua - ub;
        t     <= std_logic_vector(laaja(7 downto 0));
        kanto <= laaja(8);
      when JA   => t <= a and b;
      when TAI  => t <= a or b;
      when XTAI => t <= a xor b;
      when SIIRTO_V =>
        t     <= a(6 downto 0) & '0';
        kanto <= a(7);
      when SIIRTO_O =>
        t     <= a(7) & a(7 downto 1);     -- aritmeettinen siirto
        kanto <= a(0);
      when PIENEMPI =>
        t <= (others => '0');
        if signed(a) < signed(b) then
          t(0) <= '1';
        end if;
    end case;
  end process laskenta;

  tulos <= t;
  nolla <= '1' when t = x"00" else '0';
end architecture rtl;
-- @loppu alu

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;
use work.alu_pkg.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal op           : operaatio_t := SUMMA;
  signal a, b, tulos  : std_logic_vector(7 downto 0) := x"00";
  signal kanto, nolla : std_logic;
begin
  dut : entity work.alu
    port map (op => op, a => a, b => b, tulos => tulos, kanto => kanto,
              nolla => nolla);

  testi : process
    variable rivi : line;
    procedure laske(o : operaatio_t; x, y : std_logic_vector) is
    begin
      op <= o; a <= x; b <= y;
      wait for 1 ns;
      write(rivi, operaatio_t'image(o) & " " & to_hstring(x) & " "
                  & to_hstring(y) & " = " & to_hstring(tulos)
                  & " K=" & to_string(kanto) & " N=" & to_string(nolla));
      writeline(output, rivi);
    end procedure laske;
  begin
    laske(SUMMA,    x"F0", x"20");
    laske(EROTUS,   x"10", x"10");
    laske(EROTUS,   x"10", x"20");
    laske(XTAI,     x"AA", x"FF");
    laske(SIIRTO_O, x"81", x"00");
    laske(PIENEMPI, x"FF", x"01");      -- -1 < 1
    wait;
  end process testi;
end architecture sim;
