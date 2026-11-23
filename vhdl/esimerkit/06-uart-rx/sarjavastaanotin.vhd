-- UART-vastaanotin: 8 databittiä, ei pariteettia, 1 lopetusbitti
-- (8N1). Linja on levossa 1. Aloitusbitti 0 käynnistää vastaanoton,
-- ja jokainen bitti näytteistetään keskeltä.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- @alku entiteetti
entity sarjavastaanotin is
  generic (KELLOJA_BITTIIN : positive := 868);   -- 100 MHz / 115200
  port (
    clk        : in  std_logic;
    nollaa     : in  std_logic;
    rx         : in  std_logic;    -- tahdistettu sarjalinja
    tavu       : out std_logic_vector(7 downto 0);
    valmis     : out std_logic;    -- yhden jakson pulssi
    kehysvirhe : out std_logic     -- lopetusbitti oli 0
  );
end entity sarjavastaanotin;
-- @loppu entiteetti

architecture rtl of sarjavastaanotin is
  -- @alku tila
  type tila_t is (LEPO, ALOITUS, DATA, LOPETUS);
  signal tila      : tila_t := LEPO;
  signal ajastin   : natural range 0 to KELLOJA_BITTIIN - 1 := 0;
  signal bitti     : natural range 0 to 7 := 0;
  signal siirto    : std_logic_vector(7 downto 0) := (others => '0');
  -- @loppu tila
begin
  -- @alku prosessi
  process (clk)
  begin
    if rising_edge(clk) then
      valmis     <= '0';                -- pulssien oletusarvot
      kehysvirhe <= '0';

      if nollaa = '1' then
        tila <= LEPO;
      else
        case tila is
          when LEPO =>
            if rx = '0' then            -- aloitusbitin reuna
              ajastin <= KELLOJA_BITTIIN / 2 - 1;
              tila    <= ALOITUS;
            end if;

          when ALOITUS =>               -- aloitusbitin keskikohta
            if ajastin /= 0 then
              ajastin <= ajastin - 1;
            elsif rx = '0' then
              ajastin <= KELLOJA_BITTIIN - 1;
              bitti   <= 0;
              tila    <= DATA;
            else
              tila <= LEPO;             -- häiriöpiikki, ei aloitusta
            end if;

          when DATA =>
            if ajastin /= 0 then
              ajastin <= ajastin - 1;
            else
              ajastin <= KELLOJA_BITTIIN - 1;
              siirto  <= rx & siirto(7 downto 1);   -- LSB ensin
              if bitti = 7 then
                tila <= LOPETUS;
              else
                bitti <= bitti + 1;
              end if;
            end if;

          when LOPETUS =>
            if ajastin /= 0 then
              ajastin <= ajastin - 1;
            else
              if rx = '1' then
                tavu   <= siirto;
                valmis <= '1';
              else
                kehysvirhe <= '1';
              end if;
              tila <= LEPO;
            end if;
        end case;
      end if;
    end if;
  end process;
  -- @loppu prosessi
end architecture rtl;
