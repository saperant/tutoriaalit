-- @alku naytto
-- Kaksinumeroinen näyttö: kaksi dekooderia ja etunollan sammutus.
library ieee;
use ieee.std_logic_1164.all;

entity naytto is
  port (
    kymmenet : in  std_logic_vector(3 downto 0);
    ykkoset  : in  std_logic_vector(3 downto 0);
    vasen    : out std_logic_vector(6 downto 0);
    oikea    : out std_logic_vector(6 downto 0)
  );
end entity naytto;

architecture rakenne of naytto is
  signal vasen_raaka : std_logic_vector(6 downto 0);
begin
  -- Suora entiteetin instanssi: komponenttiesittelyä ei tarvita.
  dek_kymmenet : entity work.bcd7seg
    port map (numero => kymmenet, segmentit => vasen_raaka);

  dek_ykkoset : entity work.bcd7seg
    port map (numero => ykkoset, segmentit => oikea);

  -- Etunolla sammutetaan: "07" näytetään muodossa " 7".
  vasen <= (others => '0') when kymmenet = "0000" else vasen_raaka;
end architecture rakenne;
-- @loppu naytto

-- @alku komponentti
-- Sama rakenne vanhalla tavalla: komponenttiesittely ja instanssit.
architecture komponentit of naytto is
  component bcd7seg is
    port (
      numero    : in  std_logic_vector(3 downto 0);
      segmentit : out std_logic_vector(6 downto 0)
    );
  end component bcd7seg;

  signal vasen_raaka : std_logic_vector(6 downto 0);
begin
  dek_kymmenet : bcd7seg
    port map (numero => kymmenet, segmentit => vasen_raaka);
  dek_ykkoset : bcd7seg
    port map (numero => ykkoset, segmentit => oikea);

  vasen <= (others => '0') when kymmenet = "0000" else vasen_raaka;
end architecture komponentit;
-- @loppu komponentti
