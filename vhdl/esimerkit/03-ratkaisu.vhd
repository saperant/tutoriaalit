library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;

-- Tulostaa std_logic-tyypin ratkaisutaulukon: mikä arvo johdossa on,
-- kun kaksi ajuria ajaa sitä arvoilla rivi ja sarake.
entity testipenkki is
end entity testipenkki;

architecture sim of testipenkki is
  type arvot_t is array (natural range <>) of std_ulogic;
  constant ARVOT : arvot_t := ('0', '1', 'Z', 'L', 'H', 'X');

  -- @alku ajurit
  signal johto : std_logic;             -- ratkaistu: useita ajureita
  signal a, b  : std_ulogic := 'Z';
begin
  johto <= a;                           -- ajuri 1
  johto <= b;                           -- ajuri 2
  -- @loppu ajurit

  process
    variable rivi : line;
  begin
    write(rivi, string'("    0 1 Z L H X"));
    writeline(output, rivi);
    for i in ARVOT'range loop
      write(rivi, std_ulogic'image(ARVOT(i))(2) & " |");
      for j in ARVOT'range loop
        a <= ARVOT(i);
        b <= ARVOT(j);
        wait for 1 ns;
        write(rivi, ' ' & std_ulogic'image(johto)(2));
      end loop;
      writeline(output, rivi);
    end loop;
    -- Väylän tavallinen tilanne: yksi ajaa, muut ovat irti.
    a <= '0'; b <= 'Z';
    wait for 1 ns;
    assert johto = '0' report "ratkaisu väärin" severity failure;
    -- Ylösveto: heikko H häviää vahvalle nollalle.
    a <= 'H'; b <= '0';
    wait for 1 ns;
    assert johto = '0' report "ylösveto väärin" severity failure;
    wait;
  end process;
end architecture sim;
