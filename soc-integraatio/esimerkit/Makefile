# Pikku-SoC:n esimerkit: rekisterien generointi, ohjelmisto ja simulaatio.
#
#   make             kaikki tarkistukset ja simulaatiot (vertaa odotettuun)
#   make generoi     generoi rekisterilohkot uudelleen gen/-hakemistoon
#   make aja-dma     ajaa yhden ohjelman simulaatiossa ja näyttää tulosteen
#   make siivoa      poistaa build/-hakemiston
#
# Työkalut: Verilator 5, gcc-riscv64-unknown-elf ja Python 3 (ruff, mypy).

RAKENNUS := build
OHJELMAT := kaynnistys keskeytykset dma virheet

# @alku kaannos
CROSS   := riscv64-unknown-elf-
CFLAGS  := -march=rv32i_zicsr -mabi=ilp32 -O2 -std=gnu17 \
           -ffreestanding -fno-builtin -fno-tree-loop-distribute-patterns \
           -Wall -Wextra -Werror --param=min-pagesize=0 \
           -Isw -Igen
LDFLAGS := -nostdlib -nostartfiles -T sw/soc.ld -Wl,--gc-sections \
           -Wl,--no-warn-rwx-segments
TUKI    := sw/start.S sw/tuki.c
# @loppu kaannos

RTL := rtl/vaylat.sv gen/syscon_regs.sv gen/gpio_regs.sv \
       rtl/ydin.sv rtl/silta.sv rtl/kytkin.sv rtl/ram.sv rtl/apb_silta.sv \
       rtl/uart.sv rtl/gpio.sv rtl/clint.sv rtl/plic.sv rtl/dma.sv \
       rtl/axil_tarkistin.sv rtl/soc.sv
VFLAGS := --binary -Wall --assert -j 2

.PHONY: kaikki generoitu generoi siivoa $(addprefix aja-,$(OHJELMAT))

kaikki: generoitu $(OHJELMAT:%=$(RAKENNUS)/%.ok) \
        $(RAKENNUS)/tarkistin.ok $(RAKENNUS)/tehoalue.ok \
        $(RAKENNUS)/kaavio.ok

# Generoitujen tiedostojen on vastattava kuvauksia.
generoitu:
	ruff check --no-cache --quiet gen/rekisterit.py
	mypy --strict --no-error-summary \
	    --cache-dir=$(RAKENNUS)/mypy gen/rekisterit.py
	@mkdir -p $(RAKENNUS)/gen
	python3 gen/rekisterit.py gen/syscon.json $(RAKENNUS)/gen
	python3 gen/rekisterit.py gen/gpio.json $(RAKENNUS)/gen
	@for f in $(RAKENNUS)/gen/*; do \
	    diff -u gen/$$(basename $$f) $$f || \
	    { echo "gen/ ei ole ajan tasalla: make generoi"; exit 1; }; \
	done

generoi:
	python3 gen/rekisterit.py gen/syscon.json gen
	python3 gen/rekisterit.py gen/gpio.json gen

# @alku ohjelma
$(RAKENNUS)/%.elf: sw/%.c $(TUKI) sw/soc.h sw/tuki.h sw/soc.ld \
                   gen/syscon_regs.h gen/gpio_regs.h
	@mkdir -p $(RAKENNUS)
	$(CROSS)gcc $(CFLAGS) $(LDFLAGS) $(TUKI) $< -lgcc -o $@

$(RAKENNUS)/%.hex: $(RAKENNUS)/%.elf
	$(CROSS)objcopy -O verilog --verilog-data-width=4 $< $@
# @loppu ohjelma

$(RAKENNUS)/malli/Vtestipenkki: $(RTL) tb/testipenkki.sv
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module testipenkki \
	    -Mdir $(RAKENNUS)/malli -o Vtestipenkki $(RTL) tb/testipenkki.sv \
	    > $(RAKENNUS)/malli.log

# Simulaation tuloste verrataan odotettuun. $finish-ilmoitus poistetaan.
$(RAKENNUS)/%.ok: $(RAKENNUS)/%.hex $(RAKENNUS)/malli/Vtestipenkki \
                  odotettu/%.odotettu
	$(RAKENNUS)/malli/Vtestipenkki +ohjelma=$< \
	    | grep -v 'Verilog \$$finish' > $(RAKENNUS)/$*.tuloste
	diff -u odotettu/$*.odotettu $(RAKENNUS)/$*.tuloste
	@touch $@

$(addprefix aja-,$(OHJELMAT)): aja-%: $(RAKENNUS)/%.hex \
                                     $(RAKENNUS)/malli/Vtestipenkki
	$(RAKENNUS)/malli/Vtestipenkki +ohjelma=$<

# Protokollatarkistin: virheellinen orja on havaittava (simulaatio
# päättyy virheeseen, ja ilmoitus kertoo rikotun säännön).
$(RAKENNUS)/tarkistin.ok: rtl/vaylat.sv rtl/axil_tarkistin.sv \
                          tb/huono_orja.sv odotettu/tarkistin.odotettu
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module huono_orja \
	    -Mdir $(RAKENNUS)/tarkistin -o Vhuono_orja rtl/vaylat.sv \
	    rtl/axil_tarkistin.sv tb/huono_orja.sv > $(RAKENNUS)/tark.log
	! $(RAKENNUS)/tarkistin/Vhuono_orja > $(RAKENNUS)/tarkistin.tuloste 2>&1
	grep -o 'huono: R muuttui ennen kättelyä' \
	    $(RAKENNUS)/tarkistin.tuloste | head -1 \
	    | diff -u odotettu/tarkistin.odotettu -
	@touch $@

$(RAKENNUS)/tehoalue.ok: rtl/tehoalue.sv tb/tb_tehoalue.sv \
                         odotettu/tehoalue.odotettu
	@mkdir -p $(RAKENNUS)
	MAKEFLAGS= verilator $(VFLAGS) --top-module tb_tehoalue \
	    -Mdir $(RAKENNUS)/tehoalue -o Vtb_tehoalue rtl/tehoalue.sv \
	    tb/tb_tehoalue.sv > $(RAKENNUS)/teho.log
	$(RAKENNUS)/tehoalue/Vtb_tehoalue \
	    | grep -v 'Verilog \$$finish' > $(RAKENNUS)/tehoalue.tuloste
	diff -u odotettu/tehoalue.odotettu $(RAKENNUS)/tehoalue.tuloste
	@touch $@

# Kirjan ajoituskaavio (luku 5) tuotetaan käynnistysohjelman
# simulaatiosta: ensimmäinen kirjoitus UARTiin AXI4-Lite-puolelta
# APB-puolelle. Tulos verrataan tiedostoon kaaviot/uart-kirjoitus.json;
# PAIVITA=1 kirjoittaa sen uudelleen.
KAAVIO := python3 ../../yhteiset/kaaviot.py vcd
AXI_S := awvalid=AWVALID,awready=AWREADY,awaddr=AWADDR,wvalid=WVALID
AXI_S := $(AXI_S),wready=WREADY,wdata=WDATA,bvalid=BVALID,bready=BREADY
APB_S := psel=PSEL,penable=PENABLE,pwrite=PWRITE,paddr=PADDR
APB_S := $(APB_S),pwdata=PWDATA,pready=PREADY
TEHO_S := sammuta,kaynnista,vaihe,eristys,kello_paalla,virta
TEHO_S := $(TEHO_S),alue_nollaus_n,sisainen,lahto
$(RAKENNUS)/kaavio.ok: $(RTL) tb/testipenkki.sv $(RAKENNUS)/kaynnistys.hex \
                       kaaviot/uart-kirjoitus.json kaaviot/tehoalue.json \
                       rtl/tehoalue.sv tb/tb_tehoalue.sv
	MAKEFLAGS= verilator $(VFLAGS) --trace -DJALJITYS \
	    --top-module testipenkki -Mdir $(RAKENNUS)/jalki -o Vtestipenkki \
	    $(RTL) tb/testipenkki.sv > $(RAKENNUS)/jalki.log
	$(RAKENNUS)/jalki/Vtestipenkki +ohjelma=$(RAKENNUS)/kaynnistys.hex \
	    > /dev/null
	$(KAAVIO) $(RAKENNUS)/jalki.vcd --kello kello --alku 161 --jaksot 8 \
	    --signaalit $(AXI_S),$(APB_S) \
	    | python3 -m json.tool --indent 1 --no-ensure-ascii \
	    > $(RAKENNUS)/uart-kirjoitus.json
	rm -f $(RAKENNUS)/jalki.vcd
	if [ "$(PAIVITA)" = 1 ]; then \
	    cp $(RAKENNUS)/uart-kirjoitus.json kaaviot/; fi
	diff -u kaaviot/uart-kirjoitus.json $(RAKENNUS)/uart-kirjoitus.json
	MAKEFLAGS= verilator $(VFLAGS) --trace -DJALJITYS \
	    --top-module tb_tehoalue \
	    -Mdir $(RAKENNUS)/tehojalki -o Vtb_tehoalue rtl/tehoalue.sv \
	    tb/tb_tehoalue.sv > $(RAKENNUS)/tehojalki.log
	$(RAKENNUS)/tehojalki/Vtb_tehoalue > /dev/null
	$(KAAVIO) $(RAKENNUS)/tehoalue.vcd --kello kello --alku 8 --jaksot 16 \
	    --signaalit $(TEHO_S) \
	    | python3 -m json.tool --indent 1 --no-ensure-ascii \
	    > $(RAKENNUS)/tehoalue.json
	rm -f $(RAKENNUS)/tehoalue.vcd
	if [ "$(PAIVITA)" = 1 ]; then cp $(RAKENNUS)/tehoalue.json kaaviot/; fi
	diff -u kaaviot/tehoalue.json $(RAKENNUS)/tehoalue.json
	@touch $@

.PRECIOUS: $(RAKENNUS)/%.elf $(RAKENNUS)/%.hex

siivoa:
	rm -rf $(RAKENNUS)
