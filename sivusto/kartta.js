// Taitopuukartta: interaktiivinen kartta tutoriaalien taitopuusta.
//
// Taidon valitseminen polulle ottaa mukaan kaikki sen esitiedot, ja
// taidon poistaminen poistaa myös ne valitut taidot, jotka edellyttävät
// sitä. Valinta tallentuu osoitteen loppuun (#rooli-... tai #polku-...),
// joten polun voi jakaa linkkinä.

(() => {
  "use strict";

  const SVG = "http://www.w3.org/2000/svg";
  const TUNNIT_OP = 27;
  const TALLENNUS = "taitopuu-polku";

  const tila = {
    data: null,
    taidot: new Map(),
    jarjestys: [],
    alueIndeksi: new Map(),
    valitut: new Set(),
    rooli: null,
    tarkasteltu: null,
    esikatselu: null,
    haku: "",
    nakyma: { x: 0, y: 0, w: 1, h: 1 },
    asettelu: null,
    reitit: [],
    kiinnitetyt: new Set(),
  };

  const $ = (id) => document.getElementById(id);

  // ------------------------------------------------------------------
  // Apufunktiot

  function h(tagi, ominaisuudet, ...lapset) {
    const e = document.createElement(tagi);
    for (const [k, v] of Object.entries(ominaisuudet || {})) {
      if (v === null || v === undefined || v === false) continue;
      if (k === "luokka") e.className = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v === true ? "" : v);
    }
    for (const l of lapset.flat()) {
      if (l === null || l === undefined || l === false) continue;
      e.append(l instanceof Node ? l : document.createTextNode(String(l)));
    }
    return e;
  }

  function s(tagi, ominaisuudet) {
    const e = document.createElementNS(SVG, tagi);
    for (const [k, v] of Object.entries(ominaisuudet || {})) {
      e.setAttribute(k, v);
    }
    return e;
  }

  const luku = (n) => n.toLocaleString("fi-FI");

  function esitiedot(id) {
    const tulos = new Set();
    const pino = [...tila.taidot.get(id).edellyttaa];
    while (pino.length) {
      const t = pino.pop();
      if (!tulos.has(t)) {
        tulos.add(t);
        pino.push(...tila.taidot.get(t).edellyttaa);
      }
    }
    return tulos;
  }

  function jalkelaiset(id) {
    const tulos = new Set();
    const pino = [...tila.taidot.get(id).seuraajat];
    while (pino.length) {
      const t = pino.pop();
      if (!tulos.has(t)) {
        tulos.add(t);
        pino.push(...tila.taidot.get(t).seuraajat);
      }
    }
    return tulos;
  }

  function lisattavat(id) {
    return [id, ...esitiedot(id)].filter((t) => !tila.valitut.has(t));
  }

  function poistettavat(id) {
    return [id, ...jalkelaiset(id)].filter((t) => tila.valitut.has(t));
  }

  function roolinPolku(rooli) {
    const polku = new Set();
    for (const t of rooli.tavoitteet) {
      polku.add(t);
      for (const e of esitiedot(t)) polku.add(e);
    }
    return polku;
  }

  function avoimet() {
    return tila.jarjestys.filter((id) =>
      !tila.valitut.has(id) &&
      tila.taidot.get(id).edellyttaa.every((e) => tila.valitut.has(e)));
  }

  const opSumma = (ids) =>
    [...ids].reduce((a, id) => a + tila.taidot.get(id).laajuus, 0);

  const alueVari = (alue) => `var(--alue-${tila.alueIndeksi.get(alue)})`;

  function nimiRiveiksi(nimi, pituus = 17) {
    const sanat = nimi.split(" ");
    const rivit = [""];
    for (const sana of sanat) {
      const nyk = rivit[rivit.length - 1];
      if (nyk && (nyk + " " + sana).length > pituus && rivit.length < 2) {
        rivit.push(sana);
      } else {
        rivit[rivit.length - 1] = nyk ? nyk + " " + sana : sana;
      }
    }
    return rivit;
  }

  // ------------------------------------------------------------------
  // Valinnat

  function lisaa(id) {
    for (const t of lisattavat(id)) tila.valitut.add(t);
    tila.rooli = null;
    paivita();
  }

  function poista(id) {
    for (const t of poistettavat(id)) tila.valitut.delete(t);
    tila.rooli = null;
    paivita();
  }

  function vaihda(id) {
    if (tila.valitut.has(id)) poista(id);
    else lisaa(id);
  }

  function valitseRooli(rid) {
    const rooli = tila.data.roolit.find((r) => r.id === rid);
    if (!rooli) return;
    if (tila.rooli === rid) {
      tila.rooli = null;
    } else {
      tila.valitut = roolinPolku(rooli);
      tila.rooli = rid;
    }
    tila.tarkasteltu = null;
    paivita();
  }

  function tarkastele(id, keskita = false) {
    tila.tarkasteltu = id;
    if (keskita && id) {
      const t = tila.taidot.get(id);
      keskitaPisteeseen(t.x, t.y);
    }
    paivita();
  }

  // ------------------------------------------------------------------
  // Osoite ja tallennus

  function koodaa() {
    if (tila.rooli) return "rooli-" + tila.rooli;
    if (!tila.valitut.size) return "";
    let bitit = 0n;
    tila.jarjestys.forEach((id, i) => {
      if (tila.valitut.has(id)) bitit |= 1n << BigInt(i);
    });
    return "polku-" + bitit.toString(36);
  }

  function pura(merkkijono) {
    if (merkkijono.startsWith("rooli-")) {
      const rid = merkkijono.slice(6);
      const rooli = tila.data.roolit.find((r) => r.id === rid);
      if (rooli) {
        tila.valitut = roolinPolku(rooli);
        tila.rooli = rid;
        return true;
      }
    } else if (merkkijono.startsWith("polku-")) {
      let bitit = 0n;
      for (const merkki of merkkijono.slice(6)) {
        const arvo = parseInt(merkki, 36);
        if (Number.isNaN(arvo)) return false;
        bitit = bitit * 36n + BigInt(arvo);
      }
      tila.valitut = new Set(tila.jarjestys.filter(
        (_, i) => (bitit >> BigInt(i)) & 1n));
      // Varmistetaan, että jokaisen valitun esitiedot ovat mukana.
      for (const id of [...tila.valitut]) {
        for (const e of esitiedot(id)) tila.valitut.add(e);
      }
      tila.rooli = null;
      return true;
    }
    return false;
  }

  function tallenna() {
    const koodi = koodaa();
    try {
      history.replaceState(null, "", koodi ? "#" + koodi : location.pathname);
    } catch (_) { /* osoitetta ei voi muuttaa: ohitetaan */ }
    try {
      localStorage.setItem(TALLENNUS, koodi);
    } catch (_) { /* selaimen tallennus ei ole käytössä */ }
  }

  function lataaAlkutila() {
    const hash = decodeURIComponent(location.hash.slice(1));
    if (hash && pura(hash)) return;
    let tallennettu = null;
    try {
      tallennettu = localStorage.getItem(TALLENNUS);
    } catch (_) { /* ohitetaan */ }
    if (tallennettu !== null) {
      if (tallennettu === "" || pura(tallennettu)) return;
    }
    // Ensimmäisellä käynnillä näytetään esimerkkinä yksi roolipolku.
    pura("rooli-" + tila.data.roolit[0].id);
  }

  // ------------------------------------------------------------------
  // Piirtäminen

  const Asettelu = window.TaitopuuAsettelu;

  function piirra() {
    const svg = $("kartta");
    const { alueet, taidot } = tila.data;

    const defs = s("defs");
    const kuvio = s("pattern", {
      id: "ristikko", width: 40, height: 40, patternUnits: "userSpaceOnUse",
    });
    kuvio.append(s("circle", { cx: 20, cy: 20, r: 1.1, class: "ristikko" }));
    defs.append(kuvio);
    svg.append(defs);
    svg.append(s("rect", {
      x: -20000, y: -20000, width: 40000, height: 40000,
      fill: "url(#ristikko)", class: "ruudukko",
    }));

    const sisalto = s("g", { id: "sisalto" });
    const nippuryhma = s("g", { class: "niput" });
    const johdot = s("g", { class: "nippujohdot" });
    const reittiryhma = s("g", { class: "reitit", id: "reitit" });
    const solmuryhma = s("g", { class: "solmut", id: "solmut" });
    sisalto.append(nippuryhma, johdot, reittiryhma, solmuryhma);
    svg.append(sisalto);

    tila.asettelu = Asettelu.laske(tila.data);
    tila.nippuElementit = new Map();
    for (const nippu of tila.asettelu.niput.values()) {
      const g = s("g", { class: "nippu" });
      g.dataset.id = nippu.id;
      g.append(s("circle", {
        r: nippu.sade, class: "nippu-alusta",
        stroke: alueVari(nippu.alue),
      }));
      if (nippu.radanSade > 0) {
        g.append(s("circle", { r: nippu.radanSade, class: "rata" }));
      }
      const nimi = s("text", {
        y: -nippu.sade - 14, class: "alue-teksti", "text-anchor": "middle",
        fill: alueVari(nippu.alue),
      });
      nimi.textContent = alueet.find((a) => a.id === nippu.alue)?.nimi ||
        nippu.nimi;
      const ohje = s("title");
      ohje.textContent = "Vedä siirtääksesi nippua";
      g.append(nimi, ohje);
      nippuryhma.append(g);
      tila.nippuElementit.set(nippu.id, g);
    }

    tila.johtoElementit = tila.asettelu.nippureitit.map((n) => {
      const p = s("path", {
        class: "nippujohto",
        "stroke-width": (3 + 2.2 * n.maara).toFixed(1),
      });
      johdot.append(p);
      return p;
    });

    tila.reitit = tila.asettelu.reitit.map((r) => {
      const p = s("path", {
        class: "reitti " + (r.sisainen ? "sisainen" : "ulkoinen"),
      });
      p.dataset.a = r.a;
      p.dataset.b = r.b;
      reittiryhma.append(p);
      return { a: r.a, b: r.b, elementti: p };
    });

    for (const t of taidot) {
      const r = Asettelu.solmunSade(t.laajuus);
      const g = s("g", {
        class: "solmu " + (t.materiaalit ? "valmis" : "suunniteltu"),
        tabindex: 0,
        role: "button",
        "aria-label": `${t.nimi}, ${t.laajuus} op, taso ${t.taso}` +
          (t.materiaalit ? ", materiaali saatavilla" : ", suunnitteilla"),
      });
      g.dataset.id = t.id;
      g.append(s("circle", { r: r + 7, class: "halo" }));
      g.append(s("circle", { r, class: "pad" }));
      g.append(s("circle", {
        r: r * 0.42, class: "ydin", fill: alueVari(t.alue),
      }));
      const rivit = nimiRiveiksi(t.nimi);
      rivit.forEach((rivi, i) => {
        const teksti = s("text", { y: r + 20 + i * 17, class: "nimi" });
        teksti.textContent = rivi;
        g.append(teksti);
      });
      const op = s("text", { y: r + 20 + rivit.length * 17, class: "op" });
      op.textContent = `${t.laajuus} op`;
      g.append(op);
      solmuryhma.append(g);
      t.elementti = g;
    }
    sovellaAsettelu();

    solmuryhma.addEventListener("click", (e) => {
      const g = e.target.closest(".solmu");
      if (g && !tila.raahattiin) tarkastele(g.dataset.id);
    });
    solmuryhma.addEventListener("dblclick", (e) => {
      const g = e.target.closest(".solmu");
      if (g) vaihda(g.dataset.id);
    });
    solmuryhma.addEventListener("keydown", (e) => {
      const g = e.target.closest(".solmu");
      if (!g) return;
      if (e.key === "Enter") {
        e.preventDefault();
        tarkastele(g.dataset.id);
      } else if (e.key === " ") {
        e.preventDefault();
        vaihda(g.dataset.id);
      }
    });
    solmuryhma.addEventListener("pointerover", (e) => {
      const g = e.target.closest(".solmu");
      if (g) naytaVihje(g.dataset.id, e);
    });
    solmuryhma.addEventListener("pointermove", (e) => {
      const g = e.target.closest(".solmu");
      if (g) sijoitaVihje(e);
    });
    solmuryhma.addEventListener("pointerout", (e) => {
      const g = e.target.closest(".solmu");
      if (g && !g.contains(e.relatedTarget)) piilotaVihje();
    });
    solmuryhma.addEventListener("focusin", (e) => {
      const g = e.target.closest(".solmu");
      if (g) asetaEsikatselu(g.dataset.id);
    });
    solmuryhma.addEventListener("focusout", () => asetaEsikatselu(null));

    kytkeNippujenSiirto(nippuryhma);
  }

  // Päivittää nippujen, taitojen ja reittien sijainnit asettelusta.
  function sovellaAsettelu() {
    const as = tila.asettelu;
    for (const [id, nippu] of as.niput) {
      const g = tila.nippuElementit.get(id);
      g.setAttribute("transform",
        `translate(${nippu.x.toFixed(1)} ${nippu.y.toFixed(1)})`);
      g.dataset.x = nippu.x.toFixed(1);
      g.dataset.y = nippu.y.toFixed(1);
      g.dataset.r = nippu.sade.toFixed(1);
    }
    for (const t of tila.data.taidot) {
      const p = as.sijainnit.get(t.id);
      t.x = p.x;
      t.y = p.y;
      t.elementti.setAttribute("transform",
        `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`);
    }
    as.nippureitit.forEach((n, i) => {
      tila.johtoElementit[i].setAttribute("d", n.d);
    });
    as.reitit.forEach((r, i) => {
      tila.reitit[i].elementti.setAttribute("d", r.d);
    });
  }

  // Nippua voi raahata. Raahattu nippu jää paikalleen, ja muut niput
  // asettuvat sen ympärille simulaation avulla.
  function kytkeNippujenSiirto(nippuryhma) {
    let raahattava = null;
    nippuryhma.addEventListener("pointerdown", (e) => {
      const g = e.target.closest(".nippu");
      if (!g || e.button > 0) return;
      e.stopPropagation();
      const p = karttaPiste(e.clientX, e.clientY);
      const nippu = tila.asettelu.niput.get(g.dataset.id);
      raahattava = { id: g.dataset.id, dx: nippu.x - p.x, dy: nippu.y - p.y,
        osoitin: e.pointerId };
      g.setPointerCapture(e.pointerId);
      g.classList.add("raahattava");
      piilotaVihje();
    });
    nippuryhma.addEventListener("pointermove", (e) => {
      if (!raahattava || e.pointerId !== raahattava.osoitin) return;
      const p = karttaPiste(e.clientX, e.clientY);
      tila.kiinnitetyt.add(raahattava.id);
      const aiempi = new Map([...tila.asettelu.niput].map(
        ([id, n]) => [id, { x: n.x, y: n.y }]));
      aiempi.set(raahattava.id,
        { x: p.x + raahattava.dx, y: p.y + raahattava.dy });
      tila.asettelu = Asettelu.laske(tila.data, aiempi, tila.kiinnitetyt);
      sovellaAsettelu();
    });
    const lopeta = (e) => {
      if (!raahattava || e.pointerId !== raahattava.osoitin) return;
      tila.nippuElementit.get(raahattava.id).classList.remove("raahattava");
      raahattava = null;
    };
    nippuryhma.addEventListener("pointerup", lopeta);
    nippuryhma.addEventListener("pointercancel", lopeta);
  }

  function palautaAsettelu() {
    tila.kiinnitetyt.clear();
    tila.asettelu = Asettelu.laske(tila.data);
    sovellaAsettelu();
    sovita();
  }

  function paivitaKartta() {
    const valitut = tila.valitut;
    const avoinna = new Set(avoimet());
    const rooli = tila.data.roolit.find((r) => r.id === tila.rooli);
    const valinnaiset = new Set(rooli ? rooli.valinnaiset : []);
    let lisays = new Set();
    let poisto = new Set();
    if (tila.esikatselu) {
      if (valitut.has(tila.esikatselu)) {
        poisto = new Set(poistettavat(tila.esikatselu));
      } else {
        lisays = new Set(lisattavat(tila.esikatselu));
      }
    }
    const haku = tila.haku.trim().toLowerCase();
    const osumat = new Set();
    if (haku) {
      for (const t of tila.data.taidot) {
        const teksti = [t.nimi, t.kuvaus, t.testaus, ...t.aiheet]
          .join(" ").toLowerCase();
        if (teksti.includes(haku)) osumat.add(t.id);
      }
    }
    $("kartta").classList.toggle("himmennetty", Boolean(haku));
    $("haku-tulos").textContent = haku ? `${osumat.size} osumaa` : "";

    for (const t of tila.data.taidot) {
      const c = t.elementti.classList;
      c.toggle("valittu", valitut.has(t.id));
      c.toggle("avoin", avoinna.has(t.id));
      c.toggle("lisays", lisays.has(t.id));
      c.toggle("poisto", poisto.has(t.id));
      c.toggle("tarkasteltu", tila.tarkasteltu === t.id);
      c.toggle("valinnainen", valinnaiset.has(t.id) && !valitut.has(t.id));
      c.toggle("osuma", osumat.has(t.id));
      t.elementti.setAttribute("aria-pressed", valitut.has(t.id));
    }
    // Korostetut reitit piirretään muiden päälle.
    const korostetut = [];
    for (const r of tila.reitit) {
      const a = valitut.has(r.a);
      const c = r.elementti.classList;
      c.toggle("valittu", a && valitut.has(r.b));
      c.toggle("lisays", lisays.has(r.b) && (a || lisays.has(r.a)));
      c.toggle("poisto", poisto.has(r.b));
      if (c.contains("valittu")) korostetut.push(r.elementti);
    }
    const reittiryhma = $("reitit");
    for (const r of tila.reitit) {
      if (r.elementti.classList.contains("lisays") ||
          r.elementti.classList.contains("poisto")) {
        korostetut.push(r.elementti);
      }
    }
    for (const e of korostetut) reittiryhma.append(e);
    for (const nappi of $("roolit").children) {
      nappi.setAttribute("aria-pressed", nappi.dataset.id === tila.rooli);
    }
    paivitaLaskuri(lisays, poisto);
  }

  function paivitaLaskuri(lisays, poisto) {
    const n = tila.valitut.size;
    const op = opSumma(tila.valitut);
    const valmiit = [...tila.valitut].filter(
      (id) => tila.taidot.get(id).materiaalit).length;
    const laskuri = $("laskuri");
    laskuri.replaceChildren(
      h("b", null, luku(n)), " taitoa · ",
      h("b", null, luku(op)), " op · ",
      `≈ ${luku(op * TUNNIT_OP)} h · `,
      h("b", null, luku(valmiit)), " materiaalia valmiina");
    if (lisays.size) {
      laskuri.append(" ", h("span", { luokka: "delta" },
        `+${lisays.size} taitoa, +${opSumma(lisays)} op`));
    } else if (poisto.size) {
      laskuri.append(" ", h("span", { luokka: "delta miinus" },
        `−${poisto.size} taitoa, −${opSumma(poisto)} op`));
    }
  }

  // ------------------------------------------------------------------
  // Vihje ja esikatselu

  function asetaEsikatselu(id) {
    if (tila.esikatselu === id) return;
    tila.esikatselu = id;
    paivitaKartta();
  }

  function naytaVihje(id, e) {
    const t = tila.taidot.get(id);
    const vihje = $("vihje");
    const valittu = tila.valitut.has(id);
    const muutos = valittu ? poistettavat(id) : lisattavat(id);
    vihje.replaceChildren(
      h("strong", null, t.nimi),
      h("div", { luokka: "pieni" },
        `${t.laajuus} op · taso ${t.taso} · ` +
        (t.materiaalit ? "materiaali saatavilla" : "suunnitteilla")),
      h("div", { luokka: "pieni" }, valittu
        ? `Tuplaklikkaus poistaa ${muutos.length} taitoa polulta`
        : `Tuplaklikkaus lisää ${muutos.length} taitoa (${opSumma(muutos)} op)`));
    vihje.hidden = false;
    sijoitaVihje(e);
    asetaEsikatselu(id);
  }

  function sijoitaVihje(e) {
    const vihje = $("vihje");
    const alue = $("karttaalue").getBoundingClientRect();
    let x = e.clientX - alue.left + 16;
    let y = e.clientY - alue.top + 16;
    const w = vihje.offsetWidth;
    const korkeus = vihje.offsetHeight;
    if (x + w > alue.width - 8) x = e.clientX - alue.left - w - 16;
    if (y + korkeus > alue.height - 8) y = e.clientY - alue.top - korkeus - 16;
    vihje.style.left = `${Math.max(8, x)}px`;
    vihje.style.top = `${Math.max(8, y)}px`;
  }

  function piilotaVihje() {
    $("vihje").hidden = true;
    asetaEsikatselu(null);
  }

  // ------------------------------------------------------------------
  // Paneeli

  function alueNimi(id) {
    return tila.data.alueet.find((a) => a.id === id).nimi;
  }

  function siru(id) {
    const t = tila.taidot.get(id);
    return h("button", {
      type: "button",
      luokka: "siru" + (tila.valitut.has(id) ? " valittu" : ""),
      onclick: () => tarkastele(id, true),
    }, h("span", { luokka: "piste", style: `background:${alueVari(t.alue)}` }),
    t.nimi);
  }

  function linkki(href, otsikko, selite) {
    return h("a", {
      luokka: "linkki", href, target: "_blank", rel: "noopener",
    }, otsikko, h("span", null, selite));
  }

  function paneeliTaito(id) {
    const t = tila.taidot.get(id);
    const valittu = tila.valitut.has(id);
    const muutos = valittu ? poistettavat(id) : lisattavat(id);
    const roolit = tila.data.roolit.filter((r) => roolinPolku(r).has(id));
    const valinnaisena = tila.data.roolit.filter(
      (r) => r.valinnaiset.includes(id));
    const m = t.materiaalit;

    const toiminto = h("button", {
      type: "button",
      luokka: "nappi " + (valittu ? "vaarallinen" : "ensisijainen"),
      onclick: () => vaihda(id),
      onmouseenter: () => asetaEsikatselu(id),
      onmouseleave: () => asetaEsikatselu(null),
      onfocus: () => asetaEsikatselu(id),
      onblur: () => asetaEsikatselu(null),
    }, valittu
      ? `Poista polulta (−${muutos.length} taitoa)`
      : `Lisää polulle (+${muutos.length} taitoa, ${opSumma(muutos)} op)`);

    return [
      h("div", { luokka: "ylarivi" },
        h("span", { luokka: "piste", style: `background:${alueVari(t.alue)}` }),
        alueNimi(t.alue),
        h("button", {
          type: "button", luokka: "takaisin",
          onclick: () => tarkastele(null),
        }, "Polun yhteenveto")),
      h("h2", null, t.nimi),
      h("div", { luokka: "sirut" },
        h("span", { luokka: "merkki" + (m ? " valmis" : "") },
          m ? "Materiaali saatavilla" : "Suunnitteilla"),
        h("span", { luokka: "merkki" }, `${t.laajuus} op`),
        h("span", { luokka: "merkki" }, `taso ${t.taso}`),
        h("span", { luokka: "merkki" }, `≈ ${luku(t.laajuus * TUNNIT_OP)} h`)),
      h("p", { style: "margin-top:12px" }, t.kuvaus),
      h("div", { luokka: "toimintarivi" }, toiminto),
      m && [
        h("h3", null, "Materiaalit"),
        h("div", { luokka: "linkit" },
          m.pdf && linkki(m.pdf, "Tutoriaali", "PDF"),
          m.esimerkit && linkki(m.esimerkit, "Esimerkit ja kehityskontti",
            "zip"),
          m.codespaces && linkki(m.codespaces, "Avaa Codespacesissa",
            "GitHub"),
          linkki(m.lahde, "Lähdekoodi", "GitHub")),
        m.luvut.length > 0 && [
          h("h3", null, "Sisältö"),
          h("ol", { luokka: "lista" }, m.luvut.map((l) => h("li", null, l))),
        ],
      ],
      !m && [
        h("h3", null, "Suunniteltu sisältö"),
        h("ul", { luokka: "lista" }, t.aiheet.map((a) => h("li", null, a))),
      ],
      h("h3", null, "Edellyttää"),
      t.edellyttaa.length
        ? h("div", { luokka: "sirut" }, t.edellyttaa.map(siru))
        : h("p", null, "Ei esitietoja: hyvä aloituskohta."),
      h("h3", null, "Mahdollistaa"),
      t.seuraajat.length
        ? h("div", { luokka: "sirut" }, t.seuraajat.map(siru))
        : h("p", null, "Polun päätepiste."),
      h("h3", null, "Roolit"),
      h("div", { luokka: "sirut" },
        roolit.map((r) => h("button", {
          type: "button", luokka: "siru",
          onclick: () => valitseRooli(r.id),
        }, r.nimi)),
        valinnaisena.map((r) => h("button", {
          type: "button", luokka: "siru",
          onclick: () => valitseRooli(r.id),
        }, `${r.nimi} (valinnainen)`))),
      h("h3", null, "Tiedot"),
      h("dl", { luokka: "tieto" },
        h("dt", null, "Testaus"), h("dd", null, t.testaus),
        h("dt", null, "AMK-vastine"), h("dd", null, t.amk),
        h("dt", null, "roadmap.sh"),
        h("dd", null, t.roadmap.length
          ? t.roadmap.flatMap((r, i) => [i ? ", " : "", h("a", {
            href: `https://roadmap.sh/${r}`, target: "_blank",
            rel: "noopener",
          }, r)])
          : "–")),
    ];
  }

  function paneeliPolku() {
    const valitut = [...tila.valitut].map((id) => tila.taidot.get(id));
    const rooli = tila.data.roolit.find((r) => r.id === tila.rooli);
    const op = opSumma(tila.valitut);
    const valmiit = valitut.filter((t) => t.materiaalit).length;
    const seuraavat = avoimet().map((id) => tila.taidot.get(id))
      .sort((a, b) => (b.materiaalit ? 1 : 0) - (a.materiaalit ? 1 : 0) ||
        a.taso - b.taso);

    const tasot = new Map();
    for (const t of valitut) {
      if (!tasot.has(t.taso)) tasot.set(t.taso, []);
      tasot.get(t.taso).push(t);
    }

    const otsikko = rooli ? rooli.nimi : valitut.length ? "Oma polku" :
      "Rakenna polku";
    return [
      h("div", { luokka: "ylarivi" }, rooli ? "Roolipolku" : "Polku"),
      h("h2", null, otsikko),
      rooli && h("p", null, rooli.kuvaus),
      !valitut.length && [
        h("p", { luokka: "ohje" },
          "Valitse yläpalkista rooli tai rakenna oma polku kartalta. " +
          "Klikkaa taitoa nähdäksesi sen tiedot ja materiaalit. " +
          "Tuplaklikkaus tai välilyönti lisää taidon polulle kaikkine " +
          "esitietoineen."),
      ],
      valitut.length > 0 && h("div", { luokka: "mittarit" },
        h("div", { luokka: "mittari" }, h("b", null, luku(valitut.length)),
          h("span", null, "taitoa")),
        h("div", { luokka: "mittari" }, h("b", null, luku(op)),
          h("span", null, `op ≈ ${luku(op * TUNNIT_OP)} h`)),
        h("div", { luokka: "mittari" }, h("b", null, `${valmiit}/${valitut.length}`),
          h("span", null, "materiaalia valmiina"))),
      rooli && rooli.valinnaiset.length > 0 && [
        h("h3", null, "Valinnaiset syvennykset"),
        h("div", { luokka: "sirut" }, rooli.valinnaiset.map(siru)),
      ],
      seuraavat.length > 0 && [
        h("h3", null, valitut.length ? "Seuraavaksi avautuvat" : "Aloituskohdat"),
        h("div", { luokka: "sirut" }, seuraavat.slice(0, 12).map((t) => siru(t.id))),
      ],
      valitut.length > 0 && [
        h("h3", null, "Polun taidot opiskelujärjestyksessä"),
        h("div", { luokka: "tasot" },
          [...tasot.keys()].sort((a, b) => a - b).map((taso) =>
            h("div", { luokka: "taso-ryhma" },
              h("div", { luokka: "taso-nro" }, `TASO ${taso}`),
              h("div", { luokka: "sirut" },
                tasot.get(taso).sort((a, b) => a.nimi.localeCompare(b.nimi, "fi"))
                  .map((t) => siru(t.id)))))),
      ],
      h("h3", null, "Kaikki materiaalit"),
      h("div", { luokka: "linkit" },
        tila.data.meta.opintopolut_pdf && linkki(
          tila.data.meta.opintopolut_pdf, "Opintopolut", "PDF"),
        linkki(`${tila.data.meta.repo}/blob/main/VISIO.md`, "Projektin visio",
          "GitHub"),
        linkki(tila.data.meta.repo, "Repositorio", "GitHub")),
    ];
  }

  function paivitaPaneeli() {
    const paneeli = $("paneeli");
    const sisalto = tila.tarkasteltu
      ? paneeliTaito(tila.tarkasteltu) : paneeliPolku();
    paneeli.replaceChildren(...sisalto.flat(3).filter(Boolean));
  }

  function paivita() {
    paivitaKartta();
    paivitaPaneeli();
    tallenna();
  }

  // ------------------------------------------------------------------
  // Siirto ja zoomaus

  function asetaNakyma() {
    const n = tila.nakyma;
    $("kartta").setAttribute("viewBox", `${n.x} ${n.y} ${n.w} ${n.h}`);
  }

  function sovita() {
    // Näytetään kaikki niput pienellä marginaalilla.
    const svg = $("kartta");
    const koko = svg.getBoundingClientRect();
    const l = $("sisalto").getBBox();
    // Alareunaan jätetään tilaa laskurille ja zoomausnapeille.
    const reuna = 50;
    const ala = 160;
    let w = l.width + 2 * reuna;
    let korkeus = l.height + reuna + ala;
    const cx = l.x + l.width / 2;
    const cy = l.y - reuna + korkeus / 2;
    const suhde = koko.width / Math.max(1, koko.height);
    if (w / korkeus < suhde) w = korkeus * suhde;
    else korkeus = w / suhde;
    tila.nakyma = { x: cx - w / 2, y: cy - korkeus / 2, w, h: korkeus };
    asetaNakyma();
  }

  function zoomaa(kerroin, cx, cy) {
    const n = tila.nakyma;
    const uusiW = Math.min(Math.max(n.w * kerroin, 500), 9000);
    const k = uusiW / n.w;
    const px = cx ?? n.x + n.w / 2;
    const py = cy ?? n.y + n.h / 2;
    tila.nakyma = {
      x: px - (px - n.x) * k, y: py - (py - n.y) * k, w: n.w * k, h: n.h * k,
    };
    asetaNakyma();
  }

  function keskitaPisteeseen(x, y) {
    const n = tila.nakyma;
    tila.nakyma = { ...n, x: x - n.w / 2, y: y - n.h / 2 };
    asetaNakyma();
  }

  function karttaPiste(clientX, clientY) {
    const koko = $("kartta").getBoundingClientRect();
    const n = tila.nakyma;
    const skaala = Math.max(n.w / koko.width, n.h / koko.height);
    const ox = (koko.width * skaala - n.w) / 2;
    const oy = (koko.height * skaala - n.h) / 2;
    return {
      x: n.x - ox + (clientX - koko.left) * skaala,
      y: n.y - oy + (clientY - koko.top) * skaala,
      skaala,
    };
  }

  function kytkeSiirto() {
    const svg = $("kartta");
    const osoittimet = new Map();
    let alku = null;

    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      const p = karttaPiste(e.clientX, e.clientY);
      zoomaa(Math.exp(e.deltaY * 0.0015), p.x, p.y);
    }, { passive: false });

    svg.addEventListener("pointerdown", (e) => {
      osoittimet.set(e.pointerId, { x: e.clientX, y: e.clientY });
      tila.raahattiin = false;
      alku = { ...tila.nakyma, cx: e.clientX, cy: e.clientY };
      if (osoittimet.size === 2) {
        const [a, b] = [...osoittimet.values()];
        alku.etaisyys = Math.hypot(a.x - b.x, a.y - b.y);
        alku.keski = karttaPiste((a.x + b.x) / 2, (a.y + b.y) / 2);
      }
    });

    svg.addEventListener("pointermove", (e) => {
      if (!osoittimet.has(e.pointerId) || !alku) return;
      osoittimet.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (osoittimet.size === 2 && alku.etaisyys) {
        const [a, b] = [...osoittimet.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        tila.nakyma = { x: alku.x, y: alku.y, w: alku.w, h: alku.h };
        zoomaa(alku.etaisyys / Math.max(d, 1), alku.keski.x, alku.keski.y);
        tila.raahattiin = true;
        return;
      }
      const dx = e.clientX - alku.cx;
      const dy = e.clientY - alku.cy;
      if (!tila.raahattiin && Math.hypot(dx, dy) < 4) return;
      if (!tila.raahattiin) {
        tila.raahattiin = true;
        svg.setPointerCapture(e.pointerId);
        svg.classList.add("raahaus");
        piilotaVihje();
      }
      const skaala = karttaPiste(0, 0).skaala;
      tila.nakyma = { x: alku.x - dx * skaala, y: alku.y - dy * skaala,
        w: alku.w, h: alku.h };
      asetaNakyma();
    });

    const lopeta = (e) => {
      osoittimet.delete(e.pointerId);
      svg.classList.remove("raahaus");
      if (osoittimet.size === 0) {
        alku = null;
        // Klikkaustapahtuma tulee pointerupin jälkeen: nollataan vasta sen
        // jälkeen, jotta raahaus ei valitse taitoa.
        setTimeout(() => { tila.raahattiin = false; }, 0);
      }
    };
    svg.addEventListener("pointerup", lopeta);
    svg.addEventListener("pointercancel", lopeta);

    svg.addEventListener("keydown", (e) => {
      if (e.target !== svg) return;
      const n = tila.nakyma;
      const askel = n.w * 0.08;
      const siirrot = {
        ArrowLeft: [-askel, 0], ArrowRight: [askel, 0],
        ArrowUp: [0, -askel], ArrowDown: [0, askel],
      };
      if (siirrot[e.key]) {
        e.preventDefault();
        const [dx, dy] = siirrot[e.key];
        tila.nakyma = { ...n, x: n.x + dx, y: n.y + dy };
        asetaNakyma();
      } else if (e.key === "+" || e.key === "=") {
        zoomaa(0.8);
      } else if (e.key === "-") {
        zoomaa(1.25);
      }
    });

    $("lahenna").addEventListener("click", () => zoomaa(0.75));
    $("loitonna").addEventListener("click", () => zoomaa(1.33));
    $("sovita").addEventListener("click", sovita);
    $("jarjesta").addEventListener("click", palautaAsettelu);
    window.addEventListener("resize", sovita);
  }

  // ------------------------------------------------------------------
  // Käynnistys

  function kytkeOhjaimet() {
    const roolit = $("roolit");
    for (const r of tila.data.roolit) {
      const nappi = h("button", {
        type: "button", luokka: "rooli-nappi", "aria-pressed": "false",
        title: r.kuvaus, onclick: () => valitseRooli(r.id),
      }, r.nimi);
      nappi.dataset.id = r.id;
      roolit.append(nappi);
    }

    const haku = $("haku");
    haku.addEventListener("input", () => {
      tila.haku = haku.value;
      paivitaKartta();
    });
    haku.addEventListener("keydown", (e) => {
      if (e.key !== "Enter") return;
      const ensimmainen = tila.data.taidot.find(
        (t) => t.elementti.classList.contains("osuma"));
      if (ensimmainen) tarkastele(ensimmainen.id, true);
    });

    $("tyhjenna").addEventListener("click", () => {
      tila.valitut.clear();
      tila.rooli = null;
      tila.tarkasteltu = null;
      paivita();
    });

    $("kopioi").addEventListener("click", async () => {
      const nappi = $("kopioi");
      try {
        await navigator.clipboard.writeText(location.href);
        nappi.textContent = "Linkki kopioitu";
      } catch (_) {
        nappi.textContent = "Kopioi osoiteriviltä";
      }
      setTimeout(() => { nappi.textContent = "Kopioi linkki"; }, 2000);
    });

    window.addEventListener("hashchange", () => {
      const hash = decodeURIComponent(location.hash.slice(1));
      if (hash && hash !== koodaa() && pura(hash)) paivita();
    });
  }

  function alusta(data) {
    tila.data = data;
    for (const t of data.taidot) tila.taidot.set(t.id, t);
    tila.jarjestys = data.taidot.map((t) => t.id);
    data.alueet.forEach((a) => tila.alueIndeksi.set(a.id, a.indeksi));
    const valmiit = data.taidot.filter((t) => t.materiaalit).length;
    $("tunnus-ala").textContent =
      `${data.taidot.length} taitoa · ${valmiit} valmiina`;

    piirra();
    kytkeOhjaimet();
    kytkeSiirto();
    sovita();
    lataaAlkutila();
    paivita();
    document.documentElement.dataset.valmis = "true";
  }

  fetch("taitopuu.json")
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then(alusta)
    .catch((virhe) => {
      $("paneeli").replaceChildren(
        h("h2", null, "Karttaa ei voitu ladata"),
        h("p", null, `Tiedoston taitopuu.json lataus epäonnistui (${virhe.message}). ` +
          "Jos avasit sivun suoraan tiedostosta, käynnistä paikallinen " +
          "palvelin: make -C sivusto palvele."));
    });
})();
