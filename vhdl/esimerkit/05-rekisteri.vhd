library ieee;
use ieee.std_logic_1164.all;

-- Sama rekisteri kahdella nollaustavalla: arkkitehtuuri valitsee.
entity rekisteri is
  port (
    clk      : in  std_logic;
    nollaa   : in  std_logic;
    sallittu : in  std_logic;
    d        : in  std_logic_vector(7 downto 0);
    q        : out std_logic_vector(7 downto 0)
  );
end entity rekisteri;

-- @alku synkroninen
-- Synkroninen nollaus: herkkyyslistassa on vain kello, ja nollaus on
-- tavallinen ehto reunan sisällä.
architecture synkroninen of rekisteri is
begin
  process (clk)
  begin
    if rising_edge(clk) then
      if nollaa = '1' then
        q <= (others => '0');
      elsif sallittu = '1' then
        q <= d;                         -- muulloin q pitää arvonsa
      end if;
    end if;
  end process;
end architecture synkroninen;
-- @loppu synkroninen

-- @alku asynkroninen
-- Asynkroninen nollaus: nollaus on herkkyyslistassa ja tarkistetaan
-- ennen kellon reunaa, joten se vaikuttaa ilman kelloakin.
architecture asynkroninen of rekisteri is
begin
  process (clk, nollaa)
  begin
    if nollaa = '1' then
      q <= (others => '0');
    elsif rising_edge(clk) then
      if sallittu = '1' then
        q <= d;
      end if;
    end if;
  end process;
end architecture asynkroninen;
-- @loppu asynkroninen

library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  signal clk      : std_logic := '0';
  signal nollaa   : std_logic := '0';
  signal sallittu : std_logic := '1';
  signal d        : std_logic_vector(7 downto 0) := x"5A";
  signal q_s, q_a : std_logic_vector(7 downto 0);

  procedure tulosta(otsikko : string; s, a : std_logic_vector) is
    variable rivi : line;
  begin
    write(rivi, otsikko & " synkroninen " & to_hstring(s) &
                ", asynkroninen " & to_hstring(a));
    writeline(output, rivi);
  end procedure tulosta;
begin
  u_s : entity work.rekisteri(synkroninen)
    port map (clk => clk, nollaa => nollaa, sallittu => sallittu,
              d => d, q => q_s);
  u_a : entity work.rekisteri(asynkroninen)
    port map (clk => clk, nollaa => nollaa, sallittu => sallittu,
              d => d, q => q_a);

  testi : process
    procedure reuna is
    begin
      clk <= '1'; wait for 5 ns;
      clk <= '0'; wait for 5 ns;
    end procedure reuna;
  begin
    reuna;
    tulosta("ladattu:           ", q_s, q_a);
    sallittu <= '0';
    d        <= x"FF";
    reuna;
    tulosta("ei sallintaa:      ", q_s, q_a);
    nollaa <= '1';                      -- kello ei käy
    wait for 20 ns;
    tulosta("nollaus, ei kelloa:", q_s, q_a);
    reuna;
    tulosta("reunan jälkeen:    ", q_s, q_a);
    assert q_s = x"00" and q_a = x"00"
      report "nollaus ei toiminut" severity failure;
    wait;
  end process testi;
end architecture sim;
