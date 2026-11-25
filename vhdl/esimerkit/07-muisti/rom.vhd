library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ROM: sisältö lasketaan funktiolla elaboroinnissa ja tallentuu
-- vakioon. Tässä neliötaulukko: osoite i antaa arvon i * i.
entity nelio_rom is
  port (
    clk    : in  std_logic;
    osoite : in  natural range 0 to 15;
    arvo   : out unsigned(7 downto 0)
  );
end entity nelio_rom;

architecture rtl of nelio_rom is
  -- @alku rom
  type taulu_t is array (0 to 15) of unsigned(7 downto 0);

  function alusta return taulu_t is
    variable t : taulu_t;
  begin
    for i in t'range loop
      t(i) := to_unsigned(i * i, 8);
    end loop;
    return t;
  end function alusta;

  constant TAULU : taulu_t := alusta;
begin
  process (clk)
  begin
    if rising_edge(clk) then
      arvo <= TAULU(osoite);
    end if;
  end process;
  -- @loppu rom
end architecture rtl;
