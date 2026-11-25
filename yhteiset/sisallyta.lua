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

väliin jäävät rivit. Kommenttimerkiksi kelpaa kielen mukaan `//`, `#`,
`--`, `;`, `/*` tai `<!--` (esim. `# @alku nimi` Pythonissa, `<!-- @alku
nimi -->` HTML:ssä; nimen jälkeen välilyönti). Merkintärivit poistetaan
lopullisesta tekstistä. Valitun osan yhteinen sisennys poistetaan.

Pitkästä tulosteesta voi näyttää osan koodinsa vieressä ilman merkintöjä
tiedostossa (odotettua tulostetta verrataan sellaisenaan):

    ```{.tuloste tiedosto="esimerkit/ajo.odotettu" rivit="3-8"}
    ```

    ```{.tuloste tiedosto="esimerkit/ajo.odotettu" alkaen="== vaihe 2"
        asti="valmis"}
    ```

`rivit="A-B"` valitsee rivit A–B (1 = ensimmäinen; `"5-"` loppuun asti).
`alkaen` valitsee ensimmäisestä rivistä, joka sisältää annetun tekstin,
ja `asti` päättää ensimmäiseen sen jälkeiseen riviin, joka sisältää
annetun tekstin (molemmat rivit tulevat mukaan). Jos tekstiä ei löydy tai
rivialue on tiedoston ulkopuolella, rakennus pysähtyy virheeseen, joten
tulosteen muuttuminen ei jää huomaamatta.

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

-- Merkintärivi: kommenttimerkki (//, #, --, ;, /* tai <!--) ja @alku tai
-- @loppu.
local function merkinta(rivi, sana)
  return rivi:match("^%s*[/#;%-<!*]+%s*" .. sana .. "%s+(%S+)")
end

local function on_merkinta(rivi)
  return merkinta(rivi, "@alku") or merkinta(rivi, "@loppu")
end

local function valitse_osa(kaikki, nimi, polku)
  local tulos, sisalla, loytyi = {}, false, false
  for _, rivi in ipairs(kaikki) do
    local alku = merkinta(rivi, "@alku")
    local loppu = merkinta(rivi, "@loppu")
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

-- rivit="A-B": rivit A–B, "A-" loppuun asti.
local function valitse_rivit(lista, alue, polku)
  local a, b = alue:match("^(%d+)%-(%d*)$")
  a = tonumber(a)
  b = (b ~= nil and b ~= "") and tonumber(b) or #lista
  if not a or a < 1 or b < a or b > #lista then
    error("sisallyta.lua: rivit=\"" .. alue .. "\" ei kelpaa (tiedostossa " ..
          #lista .. " riviä): " .. polku)
  end
  local tulos = {}
  for i = a, b do table.insert(tulos, lista[i]) end
  return tulos
end

-- alkaen/asti: rajaus rivien sisällön mukaan (kirjaimellinen teksti).
local function valitse_kohta(lista, alkaen, asti, polku)
  local a, b = 1, #lista
  if alkaen then
    a = nil
    for i, rivi in ipairs(lista) do
      if rivi:find(alkaen, 1, true) then a = i break end
    end
    if not a then
      error("sisallyta.lua: alkaen=\"" .. alkaen .. "\" ei löydy: " .. polku)
    end
  end
  if asti then
    b = nil
    for i = a, #lista do
      if lista[i]:find(asti, 1, true) then b = i break end
    end
    if not b then
      error("sisallyta.lua: asti=\"" .. asti .. "\" ei löydy: " .. polku)
    end
  end
  local tulos = {}
  for i = a, b do table.insert(tulos, lista[i]) end
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

-- Sarkaimet välilyönneiksi 4 merkin välein, kuten testaaja ne laskee
-- (Go-koodi sisennetään sarkaimin; PDF:n Verbatim käyttäisi leveyttä 8).
local function laajenna_sarkaimet(rivi)
  if not rivi:find("\t") then return rivi end
  local tulos, sarake = {}, 0
  for merkki in rivi:gmatch(utf8.charpattern) do
    if merkki == "\t" then
      local maara = 4 - sarake % 4
      table.insert(tulos, string.rep(" ", maara))
      sarake = sarake + maara
    else
      table.insert(tulos, merkki)
      sarake = sarake + 1
    end
  end
  return table.concat(tulos)
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

  local alue = lohko.attributes["rivit"]
  if alue then valitut = valitse_rivit(valitut, alue, polku) end
  local alkaen, asti = lohko.attributes["alkaen"], lohko.attributes["asti"]
  if alkaen or asti then
    valitut = valitse_kohta(valitut, alkaen, asti, polku)
  end

  for i, rivi in ipairs(valitut) do
    valitut[i] = laajenna_sarkaimet(rivi)
  end
  lohko.text = table.concat(valitut, "\n")
  lohko.attributes["tiedosto"] = nil
  lohko.attributes["osa"] = nil
  lohko.attributes["rivit"] = nil
  lohko.attributes["alkaen"] = nil
  lohko.attributes["asti"] = nil

  -- Tulosteet näytetään ilman syntaksikorostusta ja PDF:ssä omalla
  -- tyylillään (ympäristö `tuloste` on määritelty tiedostossa tyyli.tex).
  if lohko.classes:includes("tuloste") then
    if FORMAT:match("latex") then
      return pandoc.RawBlock("latex",
        "\\begin{tuloste}\n" .. lohko.text .. "\n\\end{tuloste}")
    end
    lohko.classes = pandoc.List({ "text" })
  end
  return lohko
end
