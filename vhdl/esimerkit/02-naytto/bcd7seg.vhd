-- @alku dekooderi
-- BCD-numero seitsensegmenttinäytön segmenteiksi. Bitit ovat
-- järjestyksessä g f e d c b a, ja 1 sytyttää segmentin. Kelvoton
-- syöte (10–15) näytetään viivana.
library ieee;
use ieee.std_logic_1164.all;

entity bcd7seg is
  port (
    numero    : in  std_logic_vector(3 downto 0);
    segmentit : out std_logic_vector(6 downto 0)
  );
end entity bcd7seg;

architecture rtl of bcd7seg is
begin
  with numero select segmentit <=
    "0111111" when "0000",
    "0000110" when "0001",
    "1011011" when "0010",
    "1001111" when "0011",
    "1100110" when "0100",
    "1101101" when "0101",
    "1111101" when "0110",
    "0000111" when "0111",
    "1111111" when "1000",
    "1101111" when "1001",
    "1000000" when others;
end architecture rtl;
-- @loppu dekooderi
