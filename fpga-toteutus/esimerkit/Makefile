# FPGA-toteutuksen esimerkkien synteesi- ja sijoitteluvuo iCE40 UP5K
# -piirille (iCEBreaker-kortti). Simuloinnin testaa yhteinen testaaja;
# tämä Makefile ajaa Yosysin ja nextpnr:n ja vertaa raporttien
# tiivistelmät tiedostoihin raportit/*.odotettu.
#
#   make           kaikki vuot ja tarkistukset
#   make vilkku    vilkun bittivirta rakennus/vilkku.bin
#   make siivoa    poistaa käännöstuotteet

R      := rakennus
VUO    := bash tyokalut/vuo.sh
RAP    := python3 tyokalut/raportti.py
UART   := 10-uart-debug/uart_rx.sv 10-uart-debug/uart_tx.sv \
          10-uart-debug/debug_ylin.sv

RAPORTIT := vilkku kertyma muisti-synk muisti-komb kertoja-dsp \
            kertoja-lut liukuhihna-1 liukuhihna-2 liukuhihna-1-retime \
            siemenet pll kaksi-kelloa suodin-rinnakkain suodin-jaettu \
            debug

.PHONY: kaikki tyokalut siivoa $(RAPORTIT)
kaikki: tyokalut $(RAPORTIT)

# Apuohjelmien laatu, jos työkalut ovat asennettuina.
tyokalut:
	@if command -v ruff > /dev/null; then \
	    ruff check -q tyokalut/raportti.py; fi
	@if command -v mypy > /dev/null; then \
	    mypy --strict --no-error-summary tyokalut/raportti.py; fi
	@if command -v shellcheck > /dev/null; then \
	    shellcheck tyokalut/vuo.sh; fi

# Tiivistelmä verrataan odotettuun: $(call vertaa,nimi)
vertaa = diff -u raportit/$(1).odotettu $(R)/$(1).tulos

# @alku bittivirta
$(R)/vilkku.json: 01-vilkku/vilkku.sv
	@mkdir -p $(R)
	yosys -q -p 'read_verilog -sv $<; synth_ice40 -top vilkku -json $@'

$(R)/vilkku.asc: $(R)/vilkku.json 01-vilkku/icebreaker.pcf
	nextpnr-ice40 --up5k --package sg48 --freq 12 -q --json $< \
	    --pcf 01-vilkku/icebreaker.pcf --asc $@

$(R)/vilkku.bin: $(R)/vilkku.asc
	icepack $< $@
# @loppu bittivirta

vilkku: $(R)/vilkku.bin
	@$(VUO) vilkku-raportti vilkku 01-vilkku/vilkku.sv "" \
	    "--freq 12 --pcf 01-vilkku/icebreaker.pcf"
	@{ $(RAP) vilkku $(R)/vilkku-raportti.stat.json \
	      $(R)/vilkku-raportti.pnr.json --solut-alle 40 --fmax-yli 50; \
	   echo "bittivirta: $$(stat -c %s $(R)/vilkku.bin) tavua"; \
	 } > $(R)/vilkku.tulos
	@$(call vertaa,vilkku)

kertyma:
	@$(VUO) kertyma kertyma 02-kertyma/kertyma.sv "" "--freq 12"
	@$(RAP) kertyma $(R)/kertyma.stat.json $(R)/kertyma.pnr.json \
	    --solut-alle 30 --fmax-yli 60 > $(R)/kertyma.tulos
	@$(call vertaa,kertyma)

muisti-synk:
	@$(VUO) muisti-synk muisti 04-muisti/muisti.sv "" "--freq 12"
	@$(RAP) muisti-synk $(R)/muisti-synk.stat.json \
	    $(R)/muisti-synk.pnr.json --solut-alle 80 > $(R)/muisti-synk.tulos
	@$(call vertaa,muisti-synk)

muisti-komb:
	@$(VUO) muisti-komb muisti 04-muisti/muisti.sv "" "--freq 12" \
	    SYNKRONINEN=0
	@$(RAP) muisti-komb $(R)/muisti-komb.stat.json \
	    $(R)/muisti-komb.pnr.json --solut-yli 2000 > $(R)/muisti-komb.tulos
	@$(call vertaa,muisti-komb)

kertoja-dsp:
	@$(VUO) kertoja-dsp kertoja 04-kertoja/kertoja.sv "-dsp" "--freq 12"
	@$(RAP) kertoja-dsp $(R)/kertoja-dsp.stat.json \
	    $(R)/kertoja-dsp.pnr.json --solut-alle 10 > $(R)/kertoja-dsp.tulos
	@$(call vertaa,kertoja-dsp)

kertoja-lut:
	@$(VUO) kertoja-lut kertoja 04-kertoja/kertoja.sv "" "--freq 12"
	@$(RAP) kertoja-lut $(R)/kertoja-lut.stat.json \
	    $(R)/kertoja-lut.pnr.json --solut-yli 100 > $(R)/kertoja-lut.tulos
	@$(call vertaa,kertoja-lut)

# @alku liukuhihna
liukuhihna-1:
	@$(VUO) liukuhihna-1 kertoja_lh 06-liukuhihna/kertoja_lh.sv "" \
	    "--freq 12" VAIHEET=1
	@$(RAP) liukuhihna-1 $(R)/liukuhihna-1.stat.json \
	    $(R)/liukuhihna-1.pnr.json --fmax-yli 30 > $(R)/liukuhihna-1.tulos
	@$(call vertaa,liukuhihna-1)

liukuhihna-2:
	@$(VUO) liukuhihna-2 kertoja_lh 06-liukuhihna/kertoja_lh.sv "" \
	    "--freq 12" VAIHEET=2
	@$(RAP) liukuhihna-2 $(R)/liukuhihna-2.stat.json \
	    $(R)/liukuhihna-2.pnr.json --fmax-yli 45 > $(R)/liukuhihna-2.tulos
	@$(call vertaa,liukuhihna-2)

liukuhihna-1-retime:
	@$(VUO) liukuhihna-1-retime kertoja_lh 06-liukuhihna/kertoja_lh.sv \
	    "-retime" "--freq 12" VAIHEET=1
	@$(RAP) liukuhihna-1-retime $(R)/liukuhihna-1-retime.stat.json \
	    $(R)/liukuhihna-1-retime.pnr.json --fmax-yli 50 \
	    > $(R)/liukuhihna-1-retime.tulos
	@$(call vertaa,liukuhihna-1-retime)
# @loppu liukuhihna

# @alku siemenet
# Sama suunnitelma viidellä sijoittelun satunnaissiemenellä.
siemenet:
	@for s in 1 2 3 4 5; do \
	    SIEMEN=$$s $(VUO) siemen-$$s kertoja_lh \
	        06-liukuhihna/kertoja_lh.sv "" "--freq 12" VAIHEET=1 && \
	    $(RAP) "siemen $$s" $(R)/siemen-$$s.stat.json \
	        $(R)/siemen-$$s.pnr.json --fmax-yli 35 --vain-ajoitus \
	        || exit 1; \
	done > $(R)/siemenet.tulos
	@$(call vertaa,siemenet)
# @loppu siemenet

pll:
	@$(VUO) pll pll_ylin 07-pll/pll_ylin.sv "" \
	    "--freq 48 --pcf 07-pll/icebreaker.pcf"
	@$(RAP) pll $(R)/pll.stat.json $(R)/pll.pnr.json \
	    --fmax-yli clk_48=48 > $(R)/pll.tulos
	@$(call vertaa,pll)

kaksi-kelloa:
	@$(VUO) kaksi-kelloa async_fifo 08-kaksi-kelloa/async_fifo.sv "" \
	    "--freq 48"
	@$(RAP) kaksi-kelloa $(R)/kaksi-kelloa.stat.json \
	    $(R)/kaksi-kelloa.pnr.json --fmax-yli 48 > $(R)/kaksi-kelloa.tulos
	@$(call vertaa,kaksi-kelloa)

suodin-rinnakkain:
	@$(VUO) suodin-rinnakkain suodin 09-jakaminen/suodin.sv "-dsp" \
	    "--freq 12" RINNAKKAIN=1
	@$(RAP) suodin-rinnakkain $(R)/suodin-rinnakkain.stat.json \
	    $(R)/suodin-rinnakkain.pnr.json --solut-alle 150 --fmax-yli 12 \
	    > $(R)/suodin-rinnakkain.tulos
	@$(call vertaa,suodin-rinnakkain)

suodin-jaettu:
	@$(VUO) suodin-jaettu suodin 09-jakaminen/suodin.sv "-dsp" \
	    "--freq 12" RINNAKKAIN=0
	@$(RAP) suodin-jaettu $(R)/suodin-jaettu.stat.json \
	    $(R)/suodin-jaettu.pnr.json --solut-yli 150 --fmax-yli 12 \
	    > $(R)/suodin-jaettu.tulos
	@$(call vertaa,suodin-jaettu)

debug:
	@$(VUO) debug debug_ylin "$(UART)" "" "--freq 12"
	@$(RAP) debug $(R)/debug.stat.json $(R)/debug.pnr.json \
	    --solut-alle 300 --fmax-yli 12 > $(R)/debug.tulos
	@$(call vertaa,debug)

siivoa:
	rm -rf $(R)
