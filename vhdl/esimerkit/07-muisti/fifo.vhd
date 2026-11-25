library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- Synkroninen FIFO rengaspuskurina. Osoittimissa on yksi ylimääräinen
-- bitti, jolla täysi ja tyhjä jono erotetaan toisistaan. Jonon
-- ensimmäinen sana näkyy lähdössä jo ennen lukua, ja lue kuittaa sen.
entity fifo is
  generic (
    LEVEYS    : positive := 8;
    OSOITEBIT : positive := 3             -- syvyys 2**OSOITEBIT sanaa
  );
  port (
    clk      : in  std_logic;
    nollaa   : in  std_logic;
    kirjoita : in  std_logic;
    k_data   : in  std_logic_vector(LEVEYS - 1 downto 0);
    taynna   : out std_logic;
    lue      : in  std_logic;
    l_data   : out std_logic_vector(LEVEYS - 1 downto 0);
    tyhja    : out std_logic
  );
end entity fifo;

architecture rtl of fifo is
  -- @alku fifo
  constant SYVYYS : positive := 2 ** OSOITEBIT;
  type muisti_t is array (0 to SYVYYS - 1)
    of std_logic_vector(LEVEYS - 1 downto 0);
  signal muisti     : muisti_t;
  -- Osoittimissa on yksi lisäbitti. Alkuarvo pitää liput järkevinä
  -- myös ennen ensimmäistä nollausta.
  signal k_os, l_os : unsigned(OSOITEBIT downto 0) := (others => '0');

  alias k_paikka : unsigned(OSOITEBIT - 1 downto 0)
    is k_os(OSOITEBIT - 1 downto 0);
  alias l_paikka : unsigned(OSOITEBIT - 1 downto 0)
    is l_os(OSOITEBIT - 1 downto 0);
begin
  tyhja  <= '1' when k_os = l_os else '0';
  taynna <= '1' when k_paikka = l_paikka
                     and k_os(OSOITEBIT) /= l_os(OSOITEBIT) else '0';
  l_data <= muisti(to_integer(l_paikka));

  process (clk)
  begin
    if rising_edge(clk) then
      if nollaa = '1' then
        k_os <= (others => '0');
        l_os <= (others => '0');
      else
        if kirjoita = '1' and taynna = '0' then
          muisti(to_integer(k_paikka)) <= k_data;
          k_os <= k_os + 1;
        end if;
        if lue = '1' and tyhja = '0' then
          l_os <= l_os + 1;
        end if;
      end if;
    end if;
  end process;
  -- @loppu fifo
end architecture rtl;
