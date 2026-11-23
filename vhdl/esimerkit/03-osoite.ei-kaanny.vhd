-- Osoitelaskuri purskesiirrolle: lataa alkuosoitteen ja kasvattaa sitä
-- jokaisella siirretyllä sanalla. Väylän osoite on std_logic_vector.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity osoitelaskuri is
  port (
    clk    : in  std_logic;
    lataa  : in  std_logic;
    alku   : in  std_logic_vector(15 downto 0);
    siirto : in  std_logic;
    osoite : out std_logic_vector(15 downto 0)
  );
end entity osoitelaskuri;

architecture rtl of osoitelaskuri is
  signal laskuri : unsigned(15 downto 0) := (others => '0');
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if lataa = '1' then
        laskuri <= unsigned(alku);
      elsif siirto = '1' then
        laskuri <= laskuri + 1;
      end if;
    end if;
  end process;

  -- @alku virhe
  osoite <= laskuri;  -- @virhe: unsigned ei ole std_logic_vector
  osoite <= std_logic_vector(laskuri);
  -- @loppu virhe
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk, lataa, siirto : std_logic := '0';
  signal alku, osoite : std_logic_vector(15 downto 0) := x"0000";
begin
  dut : entity work.osoitelaskuri
    port map (clk => clk, lataa => lataa, alku => alku,
              siirto => siirto, osoite => osoite);

  testi : process
    procedure jakso is
    begin
      clk <= '1'; wait for 5 ns;
      clk <= '0'; wait for 5 ns;
    end procedure;
    variable rivi : line;
  begin
    alku <= x"1FFE"; lataa <= '1'; jakso; lataa <= '0';
    siirto <= '1'; jakso; jakso; jakso;
    write(rivi, "kolmen siirron jälkeen: " & to_hstring(osoite));
    writeline(output, rivi);
    wait;
  end process testi;
end architecture sim;
