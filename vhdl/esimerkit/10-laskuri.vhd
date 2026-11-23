-- @alku entiteetti
-- Ylöspäin laskeva laskuri, jolla on sallintasignaali. Sama piiri on
-- SystemVerilogilla RTL-suunnittelun esimerkissä 01-laskuri.sv.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity laskuri is
  generic (LEVEYS : positive := 4);
  port (
    clk      : in  std_logic;
    rst_n    : in  std_logic;     -- asynkroninen, aktiivinen alhaalla
    sallittu : in  std_logic;
    arvo     : out unsigned(LEVEYS - 1 downto 0)
  );
end entity laskuri;

architecture rtl of laskuri is
  signal r : unsigned(LEVEYS - 1 downto 0);
begin
  process (clk, rst_n)
  begin
    if rst_n = '0' then
      r <= (others => '0');
    elsif rising_edge(clk) then
      if sallittu = '1' then
        r <= r + 1;
      end if;
    end if;
  end process;
  arvo <= r;
end architecture rtl;
-- @loppu entiteetti

-- @alku testipenkki
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk       : std_logic := '0';
  signal kaynnissa : boolean := true;
  signal rst_n     : std_logic := '0';
  signal sallittu  : std_logic := '0';
  signal arvo      : unsigned(3 downto 0);
begin
  dut : entity work.laskuri
    generic map (LEVEYS => 4)
    port map (clk => clk, rst_n => rst_n, sallittu => sallittu,
              arvo => arvo);

  -- Kello: jakso 10 ns niin kauan kuin testi on käynnissä.
  clk <= not clk after 5 ns when kaynnissa;

  testi : process
    variable rivi : line;
    procedure jaksot(n : positive) is
    begin
      for i in 1 to n loop
        wait until rising_edge(clk);
      end loop;
      wait for 1 ns;
    end procedure jaksot;
  begin
    rst_n <= '1' after 12 ns;           -- reset vapautuu kellojen välissä
    wait for 12 ns;
    jaksot(1);
    sallittu <= '1';
    jaksot(3);
    write(rivi, "3 jaksoa: arvo = " & integer'image(to_integer(arvo)));
    writeline(output, rivi);

    sallittu <= '0';
    jaksot(2);
    write(rivi, "pysäytetty: arvo = " & integer'image(to_integer(arvo)));
    writeline(output, rivi);

    sallittu <= '1';
    jaksot(14);
    write(rivi, "17 jaksoa: arvo = " & integer'image(to_integer(arvo))
                & " (4 bittiä pyörähtää)");
    writeline(output, rivi);
    assert arvo = 1 report "laskurin arvo on väärä" severity failure;
    kaynnissa <= false;                 -- kello pysähtyy
    wait;
  end process testi;
end architecture sim;
-- @loppu testipenkki
