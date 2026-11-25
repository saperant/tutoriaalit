library ieee;
use ieee.std_logic_1164.all;

-- Kaksiporttinen RAM: yksi kirjoitus- ja yksi lukuportti, sama kello.
-- Rekisteröity luku on kuvio, jonka synteesi tunnistaa lohkomuistiksi.
entity ram is
  generic (
    LEVEYS : positive := 8;
    SANOJA : positive := 16
  );
  port (
    clk      : in  std_logic;
    kirjoita : in  std_logic;
    k_osoite : in  natural range 0 to SANOJA - 1;
    k_data   : in  std_logic_vector(LEVEYS - 1 downto 0);
    l_osoite : in  natural range 0 to SANOJA - 1;
    l_data   : out std_logic_vector(LEVEYS - 1 downto 0)
  );
end entity ram;

architecture rtl of ram is
  -- @alku ram
  type muisti_t is array (0 to SANOJA - 1)
    of std_logic_vector(LEVEYS - 1 downto 0);
  signal muisti : muisti_t;             -- ei nollausta

begin
  process (clk)
  begin
    if rising_edge(clk) then
      if kirjoita = '1' then
        muisti(k_osoite) <= k_data;
      end if;
      l_data <= muisti(l_osoite);       -- vanha arvo, jos sama osoite
    end if;
  end process;
  -- @loppu ram
end architecture rtl;
