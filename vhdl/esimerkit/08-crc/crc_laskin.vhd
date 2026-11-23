-- @alku laskin
-- Viestin CRC tavu kerrallaan. Viestin pituus on enintään MAKSIMI
-- tavua; pituuslaskurin leveys lasketaan paketin funktiolla.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.crc_pkg.all;

entity crc_laskin is
  generic (MAKSIMI : positive := 64);
  port (
    clk    : in  std_logic;
    aloita : in  std_logic;                -- nollaa uutta viestiä varten
    kelpo  : in  std_logic;
    tavu   : in  tavu_t;
    crc    : out tavu_t;
    pituus : out unsigned(bitit(MAKSIMI + 1) - 1 downto 0)
  );
end entity crc_laskin;

architecture rtl of crc_laskin is
  signal tila     : tavu_t := ALKUARVO;
  signal laskettu : unsigned(pituus'range) := (others => '0');
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if aloita = '1' then
        tila     <= ALKUARVO;
        laskettu <= (others => '0');
      elsif kelpo = '1' then
        tila     <= crc8(tila, tavu);
        laskettu <= laskettu + 1;
      end if;
    end if;
  end process;

  crc    <= tila;
  pituus <= laskettu;
end architecture rtl;
-- @loppu laskin
