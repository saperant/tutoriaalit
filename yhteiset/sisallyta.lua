--[[
Pandoc-suodatin, joka sisällyttää koodilohkoihin tiedostojen sisällön.

Käyttö Markdownissa:

    ```{.cpp tiedosto="esimerkit/hei.cpp"}
    ```

    ```{.cpp tiedosto="esimerkit/hei.cpp" osa="paaohjelma"}
    ```

    ```{.tuloste tiedosto="esimerkit/hei.odotettu"}
    ```

Attribuutti `osa` valitsee tiedostosta merkintöjen

    // @alku nimi
    ...
    // @loppu nimi

väliin jäävät rivit. Kaikki @alku/@loppu-merkintärivit poistetaan
lopullisesta tekstistä. Valitun osan yhteinen sisennys poistetaan.

Lohkon oma sisältö korvataan tiedoston sisällöllä, joten koodia ei
kirjoiteta Markdowniin käsin. Näin kaikki näytetty koodi on samaa
koodia, joka käännetään ja testataan.
]]

local function lue(polku)
  local f = io.open(polku, "r")
  if not f then
    error("sisallyta.lua: tiedostoa ei löydy: " .. polku)
  end
  local sisalto = f:read("a")
  f:close()
  return sisalto
end

local function rivit(teksti)
  local tulos = {}
  for rivi in (teksti .. "\n"):gmatch("(.-)\r?\n") do
    table.insert(tulos, rivi)
  end
  -- Poistetaan tiedoston lopun tyhjät rivit.
  while #tulos > 0 and tulos[#tulos]:match("^%s*$") do
    table.remove(tulos)
  end
  return tulos
end

local function on_merkinta(rivi)
  return rivi:match("^%s*//%s*@alku%s") or rivi:match("^%s*//%s*@loppu%s")
end

local function valitse_osa(kaikki, nimi, polku)
  local tulos, sisalla, loytyi = {}, false, false
  for _, rivi in ipairs(kaikki) do
    local alku = rivi:match("^%s*//%s*@alku%s+(%S+)")
    local loppu = rivi:match("^%s*//%s*@loppu%s+(%S+)")
    if alku == nimi then
      sisalla, loytyi = true, true
    elseif loppu == nimi then
      sisalla = false
    elseif sisalla and not on_merkinta(rivi) then
      table.insert(tulos, rivi)
    end
  end
  if not loytyi then
    error("sisallyta.lua: osaa '" .. nimi .. "' ei löydy: " .. polku)
  end
  return tulos
end

local function poista_sisennys(lista)
  local pienin = nil
  for _, rivi in ipairs(lista) do
    if not rivi:match("^%s*$") then
      local s = #rivi:match("^(%s*)")
      if pienin == nil or s < pienin then pienin = s end
    end
  end
  if pienin == nil or pienin == 0 then return lista end
  local tulos = {}
  for _, rivi in ipairs(lista) do
    table.insert(tulos, rivi:sub(pienin + 1))
  end
  return tulos
end

function CodeBlock(lohko)
  local polku = lohko.attributes["tiedosto"]
  if not polku then return nil end

  local kaikki = rivit(lue(polku))
  local valitut
  local osa = lohko.attributes["osa"]
  if osa then
    valitut = poista_sisennys(valitse_osa(kaikki, osa, polku))
  else
    valitut = {}
    for _, rivi in ipairs(kaikki) do
      if not on_merkinta(rivi) then table.insert(valitut, rivi) end
    end
  end

  lohko.text = table.concat(valitut, "\n")
  lohko.attributes["tiedosto"] = nil
  lohko.attributes["osa"] = nil

  -- Tulosteet näytetään ilman syntaksikorostusta.
  if lohko.classes:includes("tuloste") then
    lohko.classes = pandoc.List({ "text" })
  end
  return lohko
end
