-- @alku dut
-- Liukuva keskiarvo neljästä viimeisestä näytteestä. Summaa
-- päivitetään juoksevasti: uusi näyte lisätään ja vanhin vähennetään.
-- Jakaminen neljällä on aritmeettinen siirto, joka pyöristää alaspäin.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity keskiarvo is
  port (
    clk          : in  std_logic;
    nollaa       : in  std_logic;
    sisaan_kelpo : in  std_logic;
    sisaan       : in  signed(11 downto 0);
    ulos_kelpo   : out std_logic;
    ulos         : out signed(11 downto 0)
  );
end entity keskiarvo;

architecture rtl of keskiarvo is
  type ikkuna_t is array (0 to 3) of signed(11 downto 0);
  signal ikkuna : ikkuna_t;
  signal summa  : signed(13 downto 0);      -- 4 * 12 bittiä: +2 bittiä
begin
  process (clk)
    variable uusi : signed(13 downto 0);
  begin
    if rising_edge(clk) then
      ulos_kelpo <= '0';
      if nollaa = '1' then
        ikkuna <= (others => (others => '0'));
        summa  <= (others => '0');
      elsif sisaan_kelpo = '1' then
        uusi   := summa + sisaan - ikkuna(3);
        ikkuna <= sisaan & ikkuna(0 to 2);
        summa  <= uusi;
        ulos   <= resize(shift_right(uusi, 2), 12);
        ulos_kelpo <= '1';
      end if;
    end if;
  end process;
end architecture rtl;
-- @loppu dut
