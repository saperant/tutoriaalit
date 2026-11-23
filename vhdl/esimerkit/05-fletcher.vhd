-- @alku fletcher
-- Fletcher-16-tarkistussumma tavuvirrasta (RFC 1146). Jokaisella
-- tavulla summa1 kasvaa tavun verran ja summa2 summa1:n UUDEN arvon
-- verran. Muuttuja päivittyy heti, joten uusi arvo on käytettävissä
-- samassa prosessin suorituksessa.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fletcher16 is
  port (
    clk    : in  std_logic;
    nollaa : in  std_logic;
    kelpo  : in  std_logic;                 -- tavu on voimassa
    tavu   : in  std_logic_vector(7 downto 0);
    summa  : out std_logic_vector(15 downto 0)
  );
end entity fletcher16;

architecture rtl of fletcher16 is
  signal s1, s2 : natural range 0 to 254 := 0;
begin
  process (clk)
    variable uusi1 : natural range 0 to 254;
  begin
    if rising_edge(clk) then
      if nollaa = '1' then
        s1 <= 0;
        s2 <= 0;
      elsif kelpo = '1' then
        uusi1 := (s1 + to_integer(unsigned(tavu))) mod 255;
        s1 <= uusi1;
        s2 <= (s2 + uusi1) mod 255;
      end if;
    end if;
  end process;

  summa <= std_logic_vector(to_unsigned(s2, 8) & to_unsigned(s1, 8));
end architecture rtl;
-- @loppu fletcher

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant JAKSO : time := 10 ns;
  signal clk     : std_logic := '0';
  signal ajossa  : boolean := true;
  signal nollaa  : std_logic := '1';
  signal kelpo   : std_logic := '0';
  signal tavu    : std_logic_vector(7 downto 0) := x"00";
  signal summa   : std_logic_vector(15 downto 0);
begin
  clk <= not clk after JAKSO / 2 when ajossa;

  dut : entity work.fletcher16
    port map (clk => clk, nollaa => nollaa, kelpo => kelpo, tavu => tavu,
              summa => summa);

  testi : process
    variable rivi : line;
    -- @alku syota
    procedure syota(teksti : string; odotettu : std_logic_vector) is
    begin
      nollaa <= '1';
      wait until rising_edge(clk);
      nollaa <= '0';
      kelpo  <= '1';
      for i in teksti'range loop
        tavu <= std_logic_vector(
                  to_unsigned(character'pos(teksti(i)), 8));
        wait until rising_edge(clk);
      end loop;
      kelpo <= '0';
      wait until rising_edge(clk);
      write(rivi, '"' & teksti & """ -> " & to_hstring(summa));
      writeline(output, rivi);
      assert summa = odotettu report "väärä tarkistussumma"
        severity failure;
    end procedure syota;
    -- @loppu syota
  begin
    syota("abcde", x"C8F0");                -- tunnetut testiarvot
    syota("abcdef", x"2057");
    syota("abcdefgh", x"0627");
    ajossa <= false;
    wait;
  end process testi;
end architecture sim;
