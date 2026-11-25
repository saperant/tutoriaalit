# HTML ja CSS. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := html-css
KIELI   := html
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: kuvakaappaukset esimerkeistä (Chromium, ks.
# ../yhteiset/selain.cjs) ja ajoitusfunktioiden käyrät (Matplotlib,
# kuvat/piirra.py). Ajetaan käsin, ja kuvat commitoidaan.
# Tyhjä valkoinen reuna rajataan pois ImageMagickilla. Dialogin kuvassa
# on tumma taustaverho koko näkymän korkeudelta, joten se rajataan
# erikseen.
KUVAT := 01-aukiolo 02-div-sivu 02-semanttinen 03-taulukko 03-upotukset \
         04-tilaus 04-virheet 05-fokus 05-kontrasti 06-valitsimet \
         06-spesifisyys 07-kaavio 07-pinnat 08-artikkeli 09-ylapalkki \
         09-akselit 09-joustavuus 09-ylivuoto 10-kortit 10-asettelu 10-alikehys \
         11-merkki 11-tarttuva 11-pinot 11-dialogi 12-kontti 12-fluidi \
         13-teemat 14-siirtyma 15-has
.PHONY: kuvat
kuvat:
	@for k in $(KUVAT); do \
	    sivu=esimerkit/$$k.html; [ -f $$sivu ] || sivu=esimerkit/$$k/index.html; \
	    SELAIN_KUVA=kuvat/$$k node ../yhteiset/selain.cjs $$sivu >/dev/null \
	        || exit 1; \
	done
	python3 kuvat/piirra.py
	@for f in kuvat/*.png; do \
	    convert $$f -bordercolor white -border 1 -trim +repage \
	        -strip $$f || exit 1; \
	done
	convert kuvat/11-dialogi-560.png -crop 560x270+0+0 +repage -strip \
	    kuvat/11-dialogi-560.png
