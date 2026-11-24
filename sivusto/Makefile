# Taitopuukartta (verkkosivu).
#
#   make            rakentaa sivuston hakemistoon rakennus/
#   make testaa     rakentaa ja testaa sivun selaimessa (Playwright)
#   make palvele    käynnistää paikallisen palvelimen (http://localhost:8000)
#
# Sivusto kokoaa muiden hakemistojen PDF:t, joten se rakennetaan niiden
# jälkeen.

# Riippuvuuksina on esimerkkitiedostoja (esim. .s, .c), joille Maken
# sisäänrakennetut säännöt eivät saa yrittää tehdä mitään.
MAKEFLAGS += --no-builtin-rules
.SUFFIXES:

YHTEISET := ../yhteiset
RAKENNUS := rakennus

.PHONY: kaikki testaa pdf palvele siivoa

kaikki: $(RAKENNUS)/index.html

$(RAKENNUS)/index.html: kartta.html kartta.css kartta.js asettelu.js \
                        $(wildcard $(YHTEISET)/*.py) \
                        ../opintopolut/taitopuu.toml \
                        $(wildcard ../*/*.pdf) \
                        $(shell find ../*/esimerkit ../.devcontainer -type f \
                            -not -path '*/bin/*' -not -path '*/build/*' \
                            -not -path '*/node_modules/*' -not -path '*/dist/*' \
                            -not -path '*/.gradle/*' -not -path '*/target/*' \
                            -not -path '*/obj_dir/*' -not -path '*/test-results/*')
	python3 $(YHTEISET)/sivusto.py .. . $(RAKENNUS)

testaa: $(RAKENNUS)/index.html
	@if node -e "require('playwright')" 2>/dev/null; then \
	    node testaa.cjs $(RAKENNUS); \
	else \
	    echo "Playwright puuttuu: sivun selaintestit ohitetaan."; \
	fi

# Juurihakemiston "make pdf" käy läpi kaikki hakemistot; sivustolla ei
# ole omaa PDF:ää.
pdf:

palvele: $(RAKENNUS)/index.html
	python3 -m http.server 8000 --directory $(RAKENNUS)

siivoa:
	rm -rf $(RAKENNUS)
