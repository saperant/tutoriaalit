# HTML ja CSS. Kohteet: ks. ../yhteiset/paketti.mk.
NIMI    := html-css
KIELI   := html
RAKENNE := taito
include ../yhteiset/paketti.mk

# Kuvitus: kuvakaappaukset muutamasta esimerkistä (Chromium, ks.
# ../yhteiset/selain.cjs). Ajetaan käsin, ja kuvat commitoidaan.
# Tyhjä valkoinen reuna rajataan pois ImageMagickilla.
KUVAT := 08-ylapalkki 09-asettelu 11-teemat
.PHONY: kuvat
kuvat:
	@for k in $(KUVAT); do \
	    sivu=esimerkit/$$k.html; [ -f $$sivu ] || sivu=esimerkit/$$k/index.html; \
	    SELAIN_KUVA=kuvat/$$k node ../yhteiset/selain.cjs $$sivu >/dev/null \
	        || exit 1; \
	done
	@for f in kuvat/*.png; do \
	    convert $$f -bordercolor white -border 1 -trim +repage \
	        -strip $$f || exit 1; \
	done
