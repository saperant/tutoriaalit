# Tarkistukset, joita yksittäisten ohjelmien testaaja ei tee:
#
#   moduuli  09-kauppa: gofmt, go vet, testit kilpailutilanteiden
#            tunnistimen kanssa, fuzz-siemenet ja vertailuajot
#   kilpa    10-laskuri.go: korjattu versio on puhdas, -kilpa ei ole
#   pako     05-allokaatiot.go: pakoanalyysin tuloste on tekstin mukainen
#   godoc    09-kauppa: go doc -tuloste vastaa tekstissä näytettyä
#
# Verkkoa ei tarvita: moduulilla ei ole ulkoisia riippuvuuksia.

GO    := $(firstword $(wildcard /usr/lib/go-1.23/bin/go) go)
GOFMT := $(dir $(GO))gofmt
export GOTOOLCHAIN := local
export GOPROXY := off
# Kilpailutilanteiden tunnistin tarvitsee C-kääntäjän (cgo).
export CC := $(firstword $(notdir $(shell command -v gcc gcc-14 clang)))
export CGO_ENABLED := 1

.PHONY: kaikki moduuli kilpa pako godoc siivoa

kaikki: moduuli kilpa pako godoc

moduuli:
	@test -z "$$($(GOFMT) -l 09-kauppa)" || { \
	    echo "gofmt: muotoile tiedostot"; $(GOFMT) -l 09-kauppa; exit 1; }
	cd 09-kauppa && $(GO) vet ./...
	cd 09-kauppa && $(GO) test -race -count=1 ./...
	cd 09-kauppa && $(GO) test -count=1 -run '^$$' -bench . \
	    -benchtime 100x ./... > /dev/null

kilpa:
	GO111MODULE=off $(GO) run -race 10-laskuri.go > /dev/null
	@if GO111MODULE=off $(GO) run -race 10-laskuri.go -kilpa \
	        > /dev/null 2> kilpa.log; then \
	    echo "10-laskuri.go -kilpa: odotettiin virhettä"; exit 1; fi; \
	grep -q "WARNING: DATA RACE" kilpa.log || { cat kilpa.log; exit 1; }

pako:
	@GO111MODULE=off $(GO) build -gcflags=-m -o /dev/null \
	    05-allokaatiot.go 2> pako.log; \
	grep -q '&Piste{...} escapes to heap' pako.log \
	    || { cat pako.log; exit 1; }

# @alku godoc
godoc:
	@cd 09-kauppa \
	&& $(GO) doc ./varasto | diff -u testdata/godoc-paketti.txt - \
	&& $(GO) doc ./varasto Varasto.Ota | diff -u testdata/godoc-ota.txt -
# @loppu godoc

siivoa:
	rm -f kilpa.log pako.log
