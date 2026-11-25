# Tarkistukset, joita yksittäisten ohjelmien testaaja ei tee:
#
#   kesto  13-kesto on Cargo-paketti: Clippy, yksikkö-, integraatio- ja
#          dokumentaatiotestit sekä rustdoc, varoitukset virheinä.
#          Lisäksi varmistetaan, että dokumentoimaton julkinen funktio
#          pysäyttää tarkistuksen.
#
# Verkkoa ei tarvita: paketilla ei ole riippuvuuksia. Käännöstuotteet
# menevät hakemistoon target/, jonka siivoa-kohde poistaa.

RUST := $(firstword $(wildcard /usr/lib/rust-1.80/bin) \
            $(dir $(shell command -v cargo)))
export PATH := $(RUST):$(PATH)
export CARGO_TERM_COLOR := never
export CARGO_TARGET_DIR := $(CURDIR)/target

.PHONY: kaikki kesto siivoa

kaikki: kesto

# @alku kesto
CARGO := cargo --offline
# Kestot vaihtelevat ajosta toiseen, joten tulosteesta verrataan vain
# testien rivit.
SIISTI := grep -E '^(test |running |   Doc-tests)' \
          | sed -E 's/; finished in .*//'

kesto:
	@cd 13-kesto \
	&& $(CARGO) clippy --quiet --all-targets -- -D warnings \
	&& $(CARGO) test -- --test-threads=1 2>&1 | $(SIISTI) \
	    | diff -u testit.odotettu - \
	&& RUSTDOCFLAGS="-D warnings" $(CARGO) doc --quiet --no-deps \
	&& test -f $(CARGO_TARGET_DIR)/doc/kesto/fn.jasenna.html
	@mkdir -p target/viallinen && cp -r 13-kesto/. target/viallinen/ \
	&& printf '\npub fn dokumentoimaton() {}\n' \
	    >> target/viallinen/src/lib.rs \
	&& cd target/viallinen \
	&& ! $(CARGO) clippy --quiet -- -D warnings 2> loki \
	&& grep -q 'missing documentation for a function' loki
	@echo "OK: kesto"
# @loppu kesto

siivoa:
	@rm -rf target 13-kesto/Cargo.lock
