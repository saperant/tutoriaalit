-- @alku paketti
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package nayte_pkg is
  -- Käsitelty näyte ja tieto siitä, leikattiinko arvo.
  type nayte_t is record
    arvo      : signed(15 downto 0);
    kyllastyi : std_logic;
  end record nayte_t;
end package nayte_pkg;
-- @loppu paketti

-- @alku sovitin
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.nayte_pkg.all;

-- 12-bittisen AD-muuntimen näyte kahden komplementin luvuksi ja
-- vahvistus kokonaisluvulla. Muunnin antaa offset-binääriä:
-- 0x000 = pienin, 0x800 = nolla, 0xFFF = suurin jännite.
entity adc_sovitin is
  generic (VAHVISTUS : integer range -128 to 127 := 16);
  port (
    raaka : in  std_logic_vector(11 downto 0);
    ulos  : out nayte_t
  );
end entity adc_sovitin;

architecture rtl of adc_sovitin is
  constant MAKSIMI : integer := 2**15 - 1;
  constant MINIMI  : integer := -2**15;
begin
  muunnos : process (all)
    variable naytteena : signed(11 downto 0);
    variable tulo      : signed(19 downto 0);     -- 12 + 8 bittiä
  begin
    -- Offset-binääristä kahden komplementtiin: ylin bitti käännetään.
    naytteena := signed(raaka xor x"800");

    -- Tulon leveys on tekijöiden leveyksien summa: tulo ei vuoda yli.
    tulo := naytteena * to_signed(VAHVISTUS, 8);

    -- Kyllästys 16 bittiin: vertailu tehdään täydellä leveydellä.
    if tulo > MAKSIMI then
      ulos.arvo      <= to_signed(MAKSIMI, 16);
      ulos.kyllastyi <= '1';
    elsif tulo < MINIMI then
      ulos.arvo      <= to_signed(MINIMI, 16);
      ulos.kyllastyi <= '1';
    else
      ulos.arvo      <= resize(tulo, 16);
      ulos.kyllastyi <= '0';
    end if;
  end process muunnos;
end architecture rtl;
-- @loppu sovitin

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use work.nayte_pkg.all;

entity testipenkki is
end entity testipenkki;

-- @alku testipenkki
architecture sim of testipenkki is
  signal raaka : std_logic_vector(11 downto 0) := x"800";
  signal ulos  : nayte_t;
begin
  dut : entity work.adc_sovitin
    generic map (VAHVISTUS => 20)
    port map (raaka => raaka, ulos => ulos);

  testi : process
    type syotteet_t is array (natural range <>) of
      std_logic_vector(11 downto 0);
    constant SYOTTEET : syotteet_t :=
      (x"800", x"801", x"7FF", x"C00", x"FFF", x"000");
    variable rivi : line;
  begin
    for i in SYOTTEET'range loop
      raaka <= SYOTTEET(i);
      wait for 1 ns;
      write(rivi, to_hstring(raaka) & " -> "
                  & integer'image(to_integer(ulos.arvo))
                  & " kyllästyi=" & to_string(ulos.kyllastyi));
      writeline(output, rivi);
    end loop;
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
