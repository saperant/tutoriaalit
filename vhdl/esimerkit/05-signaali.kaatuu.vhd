-- Fletcher-16 ilman muuttujaa: summa2 lasketaan signaalista s1, joka
-- päivittyy vasta prosessin pysähdyttyä. summa2 saa siis s1:n VANHAN
-- arvon, ja tarkistussumma on väärä.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity fletcher16 is
  port (
    clk   : in  std_logic;
    kelpo : in  std_logic;
    tavu  : in  std_logic_vector(7 downto 0);
    summa : out std_logic_vector(15 downto 0)
  );
end entity fletcher16;

architecture rtl of fletcher16 is
  signal s1, s2 : natural range 0 to 254 := 0;
begin
  -- @alku virhe
  process (clk)
  begin
    if rising_edge(clk) then
      if kelpo = '1' then
        s1 <= (s1 + to_integer(unsigned(tavu))) mod 255;
        s2 <= (s2 + s1) mod 255;            -- s1 on vielä vanha
      end if;
    end if;
  end process;
  -- @loppu virhe

  summa <= std_logic_vector(to_unsigned(s2, 8) & to_unsigned(s1, 8));
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk    : std_logic := '0';
  signal ajossa : boolean := true;
  signal kelpo  : std_logic := '0';
  signal tavu   : std_logic_vector(7 downto 0) := x"00";
  signal summa  : std_logic_vector(15 downto 0);
begin
  clk <= not clk after 5 ns when ajossa;

  dut : entity work.fletcher16
    port map (clk => clk, kelpo => kelpo, tavu => tavu, summa => summa);

  testi : process
    constant TEKSTI : string := "abcde";
  begin
    kelpo <= '1';
    for i in TEKSTI'range loop
      tavu <= std_logic_vector(to_unsigned(character'pos(TEKSTI(i)), 8));
      wait until rising_edge(clk);
    end loop;
    kelpo <= '0';
    wait until rising_edge(clk);
    ajossa <= false;
    assert summa = x"C8F0"
      report "väärä tarkistussumma " & to_hstring(summa) severity failure;
    wait;
  end process testi;
end architecture sim;
