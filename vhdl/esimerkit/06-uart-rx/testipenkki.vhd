library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  constant JAKSO  : time := 10 ns;
  constant BITTI  : positive := 16;          -- nopea simulointi
  signal clk      : std_logic := '0';
  signal ajossa   : boolean := true;
  signal nollaa   : std_logic := '1';
  signal rx       : std_logic := '1';
  signal tavu     : std_logic_vector(7 downto 0);
  signal valmis, kehysvirhe : std_logic;
begin
  clk <= not clk after JAKSO / 2 when ajossa;

  dut : entity work.sarjavastaanotin
    generic map (KELLOJA_BITTIIN => BITTI)
    port map (clk => clk, nollaa => nollaa, rx => rx, tavu => tavu,
              valmis => valmis, kehysvirhe => kehysvirhe);

  -- @alku lahetys
  -- Lähettäjän malli: kehys bitti kerrallaan oikealla bittiajalla.
  lahetin : process
    procedure laheta(t : std_logic_vector(7 downto 0);
                     lopetus : std_logic := '1') is
    begin
      rx <= '0';
      wait for BITTI * JAKSO;
      for i in 0 to 7 loop
        rx <= t(i);
        wait for BITTI * JAKSO;
      end loop;
      rx <= lopetus;
      wait for BITTI * JAKSO;
      rx <= '1';
      wait for 2 * BITTI * JAKSO;
    end procedure laheta;
  begin
    wait for 5 * JAKSO;
    nollaa <= '0';
    wait for 5 * JAKSO;
    laheta(x"4B");
    laheta(x"A5");
    laheta(x"00", lopetus => '0');          -- rikottu kehys
    laheta(x"FF");
    ajossa <= false;
    wait;
  end process lahetin;

  -- Vastaanoton seuranta: tulostetaan jokainen tapahtuma.
  seuranta : process (clk)
    variable rivi : line;
  begin
    if rising_edge(clk) then
      if valmis = '1' then
        write(rivi, "vastaanotettu " & to_hstring(tavu)
                    & " @ " & to_string(now, us));
        writeline(output, rivi);
      end if;
      if kehysvirhe = '1' then
        write(rivi, "kehysvirhe @ " & to_string(now, us));
        writeline(output, rivi);
      end if;
    end if;
  end process seuranta;
  -- @loppu lahetys
end architecture sim;
