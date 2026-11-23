-- Rengaspuskuri, jonka osoitteet kiertävät luonnostaan vain, jos
-- syvyys on kahden potenssi. Entiteetin oma assert-lause tarkistaa
-- generic-parametrit ennen kuin yksikään kellojakso on simuloitu.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- @alku tarkistus
entity rengas is
  generic (
    SYVYYS_BITTEINA : positive := 4;
    SYVYYS          : positive := 16
  );
  port (
    clk       : in  std_logic;
    kirjoita  : in  std_logic;
    data      : in  std_logic_vector(7 downto 0);
    viimeisin : out std_logic_vector(7 downto 0)
  );
begin
  assert SYVYYS = 2**SYVYYS_BITTEINA
    report "SYVYYS ei ole 2**SYVYYS_BITTEINA" severity failure;
end entity rengas;
-- @loppu tarkistus

architecture rtl of rengas is
  type muisti_t is array (0 to SYVYYS - 1)
    of std_logic_vector(7 downto 0);
  signal muisti : muisti_t;
  signal osoite : unsigned(SYVYYS_BITTEINA - 1 downto 0)
    := (others => '0');
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if kirjoita = '1' then
        muisti(to_integer(osoite)) <= data;
        osoite <= osoite + 1;               -- kiertää ympäri
      end if;
    end if;
  end process;
  viimeisin <= muisti(to_integer(osoite - 1));
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk, kirjoita : std_logic := '0';
  signal data, viimeisin : std_logic_vector(7 downto 0) := x"00";
begin
  -- @alku kaytto
  dut : entity work.rengas
    generic map (SYVYYS_BITTEINA => 4, SYVYYS => 10)    -- ristiriita
    port map (clk => clk, kirjoita => kirjoita, data => data,
              viimeisin => viimeisin);
  -- @loppu kaytto
end architecture sim;
