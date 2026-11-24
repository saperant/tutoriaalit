--[[
Pandoc-suodatin, joka antaa luvun lopun vakio-osioille oman ulkoasun
PDF:ssä (ks. tyyli.tex):

- `## Käytännössä` -osion sisältö ladotaan sävytetylle taustalle.
- `## Itsearviointi` ja sitä seuraava luettelo ladotaan tarkistuslistaksi
  laatikkoon. Otsikko ei tule sisällysluetteloon.

Muissa muodoissa suodatin ei tee mitään.
]]

local function teksti(otsikko)
  return pandoc.utils.stringify(otsikko.content)
end

function Pandoc(doc)
  if not FORMAT:match("latex") then return nil end
  local tulos = pandoc.List()
  local i = 1
  local blokit = doc.blocks
  while i <= #blokit do
    local b = blokit[i]
    if b.t == "Header" and b.level == 2 and teksti(b) == "Käytännössä" then
      tulos:insert(b)
      tulos:insert(pandoc.RawBlock("latex", "\\begin{kaytannossa}"))
      i = i + 1
      while i <= #blokit and not (blokit[i].t == "Header"
                                  and blokit[i].level <= 2) do
        tulos:insert(blokit[i])
        i = i + 1
      end
      tulos:insert(pandoc.RawBlock("latex", "\\end{kaytannossa}"))
    elseif b.t == "Header" and b.level == 2 and teksti(b) == "Itsearviointi" then
      tulos:insert(pandoc.RawBlock("latex", "\\begin{itsearviointi}"))
      i = i + 1
      while i <= #blokit and not (blokit[i].t == "Header"
                                  and blokit[i].level <= 2) do
        local s = blokit[i]
        if s.t == "BulletList" then
          tulos:insert(pandoc.RawBlock("latex", "\\begin{tarkistuslista}"))
          for _, kohta in ipairs(s.content) do
            tulos:insert(pandoc.RawBlock("latex", "\\item"))
            tulos:extend(kohta)
          end
          tulos:insert(pandoc.RawBlock("latex", "\\end{tarkistuslista}"))
        else
          tulos:insert(s)
        end
        i = i + 1
      end
      tulos:insert(pandoc.RawBlock("latex", "\\end{itsearviointi}"))
    else
      tulos:insert(b)
      i = i + 1
    end
  end
  doc.blocks = tulos
  return doc
end
