-- Sarjakertoja: aloita-pulssi käynnistää 8 jakson laskennan, ja
-- valmis kertoo tuloksen olevan voimassa. Testipenkki unohtaa
-- kellon sallinnan, joten valmis ei koskaan nouse. Ilman aikarajaa
-- simulaatio jäisi pyörimään, koska kello käy ikuisesti.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity kertoja is
  port (
    clk, sallittu : in  std_logic;
    aloita        : in  std_logic;
    a, b          : in  unsigned(7 downto 0);
    tulo          : out unsigned(15 downto 0);
    valmis        : out std_logic := '0'
  );
end entity kertoja;

architecture rtl of kertoja is
  signal kerrottava : unsigned(15 downto 0);
  signal kerroin    : unsigned(7 downto 0);
  signal summa      : unsigned(15 downto 0);
  signal jaljella   : natural range 0 to 8 := 0;
begin
  process (clk)
  begin
    if rising_edge(clk) and sallittu = '1' then
      valmis <= '0';
      if aloita = '1' then
        kerrottava <= resize(a, 16);
        kerroin    <= b;
        summa      <= (others => '0');
        jaljella   <= 8;
      elsif jaljella > 0 then
        if kerroin(0) = '1' then
          summa <= summa + kerrottava;
        end if;
        kerrottava <= shift_left(kerrottava, 1);
        kerroin    <= shift_right(kerroin, 1);
        jaljella   <= jaljella - 1;
        if jaljella = 1 then
          valmis <= '1';
        end if;
      end if;
    end if;
  end process;
  tulo <= summa;
end architecture rtl;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk      : std_logic := '0';
  signal sallittu : std_logic := '0';     -- unohtui nostaa
  signal aloita   : std_logic := '0';
  signal a, b     : unsigned(7 downto 0) := x"00";
  signal tulo     : unsigned(15 downto 0);
  signal valmis   : std_logic;
begin
  clk <= not clk after 5 ns;

  dut : entity work.kertoja
    port map (clk => clk, sallittu => sallittu, aloita => aloita,
              a => a, b => b, tulo => tulo, valmis => valmis);

  testi : process
  begin
    a <= to_unsigned(12, 8);
    b <= to_unsigned(34, 8);
    aloita <= '1';
    wait until rising_edge(clk);
    aloita <= '0';
    -- @alku odotus
    wait until valmis = '1' for 1 us;
    assert valmis = '1'
      report "aikakatkaisu: valmis ei noussut 1 us:ssa" severity failure;
    -- @loppu odotus
    assert tulo = 408 severity failure;
    std.env.finish;
  end process testi;
end architecture sim;
