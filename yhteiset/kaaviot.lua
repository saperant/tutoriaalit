--[[
Pandoc-suodatin, joka piirtää kaaviot koodilohkoista (ks. kaaviot.py).

Käyttö Markdownissa:

    ```{.ajoituskaavio otsikko="AXI-Streamin kättely"}
    {"signal": [{"name": "clk", "wave": "p...."},
                {"name": "valid", "wave": "01.0."}]}
    ```

    ```{.ajoituskaavio tiedosto="esimerkit/kattely.json" leveys="70%"}
    ```

    ```{.dot otsikko="Tilakone"}
    digraph { rankdir=LR; LEPO -> LUKU [label="start"]; }
    ```

`tiedosto` toimii kuten muissakin koodilohkoissa (sisallyta.lua lukee
sen ensin), joten kaavion lähde voi olla simulaatiosta tuotettu ja
testissä tarkistettu tiedosto. `otsikko` tulee kuvatekstiksi ja
`leveys` asettaa kuvan leveyden. Oletuksena kaavio ladotaan
luonnolliseen kokoonsa, kuitenkin enintään palstan levyisenä; näin
kaikkien ajoituskaavioiden teksti on samankokoista.

Kaaviot tallennetaan välimuistiin hakemistoon `.kaaviot/` lähteen
tiivisteen mukaan nimettyinä, joten muuttumaton kaavio piirretään vain
kerran.
]]

local hakemisto = PANDOC_SCRIPT_FILE:match("(.*/)") or "./"
local piirtaja = hakemisto .. "kaaviot.py"
local valimuisti = ".kaaviot"

local function olemassa(polku)
  local f = io.open(polku, "r")
  if f then f:close() return true end
  return false
end

local function piirra(laji, lahde, paate)
  os.execute("mkdir -p " .. valimuisti)
  local polku = valimuisti .. "/" .. pandoc.sha1(laji .. "\0" .. lahde) ..
      "." .. paate
  if not olemassa(polku) then
    local ok, virhe = pcall(pandoc.pipe, "python3",
        { piirtaja, laji, polku }, lahde)
    if not ok then
      error("kaaviot.lua: " .. laji .. "-kaavion piirtäminen epäonnistui: " ..
            tostring(virhe))
    end
  end
  return polku
end

function CodeBlock(el)
  local laji
  if el.classes:includes("ajoituskaavio") then
    laji = "ajoitus"
  elseif el.classes:includes("dot") then
    laji = "dot"
  else
    return nil
  end
  local paate = FORMAT:match("latex") and "pdf" or "svg"
  local polku = piirra(laji, el.text, paate)
  local otsikko = el.attributes["otsikko"] or ""
  local attr = {}
  local leveys = el.attributes["leveys"]
  if leveys then
    attr.width = leveys
  end
  local kuva = pandoc.Image(pandoc.Inlines(pandoc.read(otsikko, "markdown")
      .blocks[1] and pandoc.utils.blocks_to_inlines(
        pandoc.read(otsikko, "markdown").blocks) or {}),
      polku, "", pandoc.Attr("", {}, attr))
  if otsikko == "" then
    return pandoc.Para({ kuva })
  end
  return pandoc.Figure(pandoc.Plain({ kuva }),
      { pandoc.Plain(pandoc.read(otsikko, "markdown").blocks[1].content) })
end
