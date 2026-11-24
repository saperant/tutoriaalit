// Taitopuukartan asettelu.
//
// Taidot kootaan nipuiksi (oletuksena yksi nippu aluetta kohti). Nipun
// taidot sijoitetaan kiertoradalle nipun keskipisteen ympärille niin,
// että toisiaan edellyttävät taidot ovat radalla mahdollisimman lähekkäin.
// Nippujen paikat haetaan voimasimulaatiolla: nippujen väliset
// riippuvuudet vetävät nippuja toisiaan kohti ja törmäystarkistus pitää
// ne erillään. Perusta-nippu on kiinnitetty kartan keskelle.
//
// Nippujen väliset yhteydet kulkevat yhteistä runkoa pitkin: kunkin
// nippuparin välillä on yksi johdinnippu, ja yksittäinen yhteys erkanee
// siitä vasta nipun reunalla. Saman nipun sisällä vierekkäisten taitojen
// yhteys on kaari radalla ja muiden suora jänne.
//
// Moduuli on puhdasta laskentaa ilman DOMia, joten sitä voi käyttää sekä
// selaimessa (window.TaitopuuAsettelu) että Nodessa (require).

(function (vienti) {
  "use strict";

  const SOLMUVALI = 158;   // kaaren pituus vierekkäisten taitojen välillä
  const RATA_MIN = 96;     // pienin kiertoradan säde
  const REUNA = 92;        // radalta nipun reunaan (nimille tilaa)
  const VALI = 120;        // pienin tyhjä väli nippujen välillä
  const PORTTI = 54;       // johdinnipun liitoskohta radan ulkopuolella

  function solmunSade(laajuus) {
    return 9 + laajuus * 2.4;
  }

  // ----------------------------------------------------------------
  // Niput ja kiertoradat

  function muodostaNiput(data) {
    const niput = new Map();
    for (const a of data.alueet) {
      niput.set(a.id, { id: a.id, alue: a.id, nimi: a.nimi, jasenet: [] });
    }
    for (const t of data.taidot) {
      const avain = t.nippu || t.alue;
      if (!niput.has(avain)) {
        niput.set(avain, { id: avain, alue: t.alue, nimi: avain, jasenet: [] });
      }
      niput.get(avain).jasenet.push(t.id);
    }
    for (const [avain, n] of niput) {
      if (!n.jasenet.length) niput.delete(avain);
    }
    return niput;
  }

  function kehaEtaisyys(i, j, n) {
    const d = Math.abs(i - j);
    return Math.min(d, n - d);
  }

  // Järjestää nipun taidot radalle niin, että nipun sisäiset yhteydet
  // ovat mahdollisimman lyhyitä. Pienille nipuille kokeillaan kaikki
  // järjestykset (ensimmäinen taito kiinnitetty), suurille ahne haku.
  function jarjestaRata(nippu, taidot) {
    const jasenet = [...nippu.jasenet].sort((a, b) =>
      taidot.get(a).taso - taidot.get(b).taso || a.localeCompare(b));
    const n = jasenet.length;
    const sisaiset = [];
    const indeksi = new Map(jasenet.map((id, i) => [id, i]));
    for (const id of jasenet) {
      for (const e of taidot.get(id).edellyttaa) {
        if (indeksi.has(e)) sisaiset.push([indeksi.get(e), indeksi.get(id)]);
      }
    }
    if (n <= 3 || !sisaiset.length) return jasenet;

    const hinta = (paikka) => sisaiset.reduce(
      (s, [a, b]) => s + kehaEtaisyys(paikka[a], paikka[b], n) ** 2, 0);

    let paras = null;
    let parasHinta = Infinity;
    if (n <= 9) {
      const paikka = new Array(n);
      paikka[0] = 0;
      const kaytetty = new Array(n).fill(false);
      kaytetty[0] = true;
      const kay = (k) => {
        if (k === n) {
          const h = hinta(paikka);
          if (h < parasHinta) {
            parasHinta = h;
            paras = [...paikka];
          }
          return;
        }
        for (let p = 1; p < n; p++) {
          if (!kaytetty[p]) {
            kaytetty[p] = true;
            paikka[k] = p;
            kay(k + 1);
            kaytetty[p] = false;
          }
        }
      };
      kay(1);
    } else {
      paras = jasenet.map((_, i) => i);
      let parannus = true;
      while (parannus) {
        parannus = false;
        for (let i = 0; i < n; i++) {
          for (let j = i + 1; j < n; j++) {
            const koe = [...paras];
            [koe[i], koe[j]] = [koe[j], koe[i]];
            const h = hinta(koe);
            if (h < hinta(paras)) {
              paras = koe;
              parannus = true;
            }
          }
        }
      }
    }
    const tulos = new Array(n);
    paras.forEach((p, i) => { tulos[p] = jasenet[i]; });
    return tulos;
  }

  // ----------------------------------------------------------------
  // Voimasimulaatio

  function nippujenYhteydet(niput, taidot, nippuOf) {
    const maarat = new Map();
    for (const t of taidot.values()) {
      for (const e of t.edellyttaa) {
        const a = nippuOf.get(e);
        const b = nippuOf.get(t.id);
        if (a === b) continue;
        const avain = a < b ? `${a}|${b}` : `${b}|${a}`;
        maarat.set(avain, (maarat.get(avain) || 0) + 1);
      }
    }
    return [...maarat].map(([avain, maara]) => {
      const [a, b] = avain.split("|");
      return { a, b, maara };
    });
  }

  function alkuasemat(nippulista, keskus) {
    // Kultaisen kulman spiraali syvyysjärjestyksessä: deterministinen ja
    // tasaisesti levittäytyvä aloitus.
    const kultainen = Math.PI * (3 - Math.sqrt(5));
    let i = 0;
    for (const n of nippulista) {
      if (n.id === keskus) {
        n.x = 0;
        n.y = 0;
        continue;
      }
      i++;
      const r = 420 * Math.sqrt(i) + 260 * n.syvyys;
      n.x = r * Math.cos(i * kultainen);
      n.y = r * Math.sin(i * kultainen);
    }
  }

  function simuloi(nippulista, yhteydet, kierroksia, kiinnitetyt) {
    const nimella = new Map(nippulista.map((n) => [n.id, n]));
    for (let k = 0; k < kierroksia; k++) {
      const jaahdytys = 1 - k / kierroksia;
      const voima = new Map(nippulista.map((n) => [n.id, { x: 0, y: 0 }]));
      // Vetovoima yhteyksien suuntaan.
      for (const y of yhteydet) {
        const a = nimella.get(y.a);
        const b = nimella.get(y.b);
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 1;
        const tavoite = a.sade + b.sade + VALI + 60;
        const f = 0.06 * Math.sqrt(y.maara) * (d - tavoite);
        voima.get(a.id).x += (f * dx) / d;
        voima.get(a.id).y += (f * dy) / d;
        voima.get(b.id).x -= (f * dx) / d;
        voima.get(b.id).y -= (f * dy) / d;
      }
      // Hylkimisvoima kaikkien parien välillä ja törmäys.
      for (let i = 0; i < nippulista.length; i++) {
        for (let j = i + 1; j < nippulista.length; j++) {
          const a = nippulista[i];
          const b = nippulista[j];
          let dx = b.x - a.x;
          let dy = b.y - a.y;
          let d = Math.hypot(dx, dy);
          if (d < 1e-6) {
            dx = 1;
            dy = 0;
            d = 1;
          }
          const minimi = a.sade + b.sade + VALI;
          let f = -4e5 / (d * d);
          if (d < minimi) f -= 0.9 * (minimi - d);
          voima.get(a.id).x += (f * dx) / d;
          voima.get(a.id).y += (f * dy) / d;
          voima.get(b.id).x -= (f * dx) / d;
          voima.get(b.id).y -= (f * dy) / d;
        }
      }
      // Johdinniput eivät saa kulkea vieraiden nippujen läpi: nippu, jonka
      // läpi kahden muun nipun välinen johto kulkisi, työnnetään sivuun.
      for (const y of yhteydet) {
        const a = nimella.get(y.a);
        const b = nimella.get(y.b);
        const ex = b.x - a.x;
        const ey = b.y - a.y;
        const pituus2 = ex * ex + ey * ey || 1;
        for (const c of nippulista) {
          if (c === a || c === b) continue;
          const t = Math.max(0, Math.min(1,
            ((c.x - a.x) * ex + (c.y - a.y) * ey) / pituus2));
          const px = a.x + t * ex;
          const py = a.y + t * ey;
          let dx = c.x - px;
          let dy = c.y - py;
          let d = Math.hypot(dx, dy);
          if (d < 1e-6) {
            dx = -ey;
            dy = ex;
            d = Math.hypot(dx, dy) || 1;
          }
          const minimi = c.sade + 50;
          if (d < minimi) {
            const f = 0.7 * (minimi - d);
            voima.get(c.id).x += (f * dx) / d;
            voima.get(c.id).y += (f * dy) / d;
            voima.get(a.id).x -= (f * (1 - t) * dx) / d / 2;
            voima.get(a.id).y -= (f * (1 - t) * dy) / d / 2;
            voima.get(b.id).x -= (f * t * dx) / d / 2;
            voima.get(b.id).y -= (f * t * dy) / d / 2;
          }
        }
      }
      // Heikko painovoima keskustaa kohti pitää kartan koossa.
      for (const n of nippulista) {
        voima.get(n.id).x -= 0.004 * n.x;
        voima.get(n.id).y -= 0.004 * n.y;
      }
      for (const n of nippulista) {
        if (kiinnitetyt.has(n.id)) continue;
        const v = voima.get(n.id);
        const pituus = Math.hypot(v.x, v.y);
        const raja = 60 * jaahdytys + 4;
        const k2 = pituus > raja ? raja / pituus : 1;
        n.x += v.x * k2;
        n.y += v.y * k2;
      }
    }
    // Lopuksi pelkkä törmäysten purku, jotta niput eivät jää päällekkäin.
    for (let k = 0; k < 200; k++) {
      let siirretty = false;
      for (let i = 0; i < nippulista.length; i++) {
        for (let j = i + 1; j < nippulista.length; j++) {
          const a = nippulista[i];
          const b = nippulista[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const d = Math.hypot(dx, dy) || 1;
          const minimi = a.sade + b.sade + VALI * 0.75;
          if (d < minimi) {
            const s = (minimi - d) / 2 + 0.5;
            // Kiinnitetty nippu väistää vain toista kiinnitettyä.
            const pa = kiinnitetyt.has(a.id);
            const pb = kiinnitetyt.has(b.id);
            const ka = pa === pb ? 1 : pa ? 0 : 2;
            const kb = 2 - ka;
            a.x -= (s * ka * dx) / d;
            a.y -= (s * ka * dy) / d;
            b.x += (s * kb * dx) / d;
            b.y += (s * kb * dy) / d;
            siirretty = true;
          }
        }
      }
      if (!siirretty) break;
    }
  }

  // ----------------------------------------------------------------
  // Radan kierto ja sijainnit

  function asetaSolmut(nippu, taidot, sijainnit) {
    const n = nippu.rata.length;
    nippu.rata.forEach((id, i) => {
      const kulma = nippu.kierto + (2 * Math.PI * i) / n;
      sijainnit.set(id, {
        x: nippu.x + (n === 1 ? 0 : nippu.radanSade * Math.cos(kulma)),
        y: nippu.y + (n === 1 ? 0 : nippu.radanSade * Math.sin(kulma)),
      });
    });
  }

  // Kiertää jokaisen nipun radan niin, että taidot, joilla on yhteyksiä
  // muihin nippuihin, ovat niiden puolella.
  function kierraRadat(nippulista, taidot, nippuOf) {
    const nimella = new Map(nippulista.map((n) => [n.id, n]));
    for (const nippu of nippulista) {
      const n = nippu.rata.length;
      if (n === 1) {
        nippu.kierto = 0;
        continue;
      }
      const ulkoiset = [];
      nippu.rata.forEach((id, i) => {
        const t = taidot.get(id);
        for (const muu of [...t.edellyttaa, ...t.seuraajat]) {
          const toinen = nippuOf.get(muu);
          if (toinen !== nippu.id) ulkoiset.push([i, nimella.get(toinen)]);
        }
      });
      let paras = 0;
      let parasHinta = Infinity;
      for (let s = 0; s < 120; s++) {
        const kierto = (2 * Math.PI * s) / 120 - Math.PI / 2;
        let h = 0;
        for (const [i, toinen] of ulkoiset) {
          const kulma = kierto + (2 * Math.PI * i) / n;
          const x = nippu.x + nippu.radanSade * Math.cos(kulma);
          const y = nippu.y + nippu.radanSade * Math.sin(kulma);
          h += Math.hypot(toinen.x - x, toinen.y - y);
        }
        if (h < parasHinta - 1e-6) {
          parasHinta = h;
          paras = kierto;
        }
      }
      nippu.kierto = paras;
    }
  }

  // ----------------------------------------------------------------
  // Reitit

  const f1 = (v) => v.toFixed(1);

  function bezier(p0, c, p1, t) {
    const u = 1 - t;
    return {
      x: u * u * p0.x + 2 * u * t * c.x + t * t * p1.x,
      y: u * u * p0.y + 2 * u * t * c.y + t * t * p1.y,
    };
  }

  // Pahin este rungolla: nippu, jonka radan läpi tai liian läheltä käyrä
  // kulkee. Palauttaa esteen ja sen, kuinka paljon tilaa puuttuu.
  function pahinEste(p0, c, p1, esteet) {
    let pahin = null;
    for (let i = 0; i <= 40; i++) {
      const p = bezier(p0, c, p1, i / 40);
      for (const e of esteet) {
        const puute = e.radanSade + 60 - Math.hypot(p.x - e.x, p.y - e.y);
        if (puute > 0 && (!pahin || puute > pahin.puute)) {
          pahin = { este: e, puute, t: i / 40 };
        }
      }
    }
    return pahin;
  }

  // Runko on toisen asteen Bézier-käyrä. Jos suora runko kulkisi vieraan
  // nipun läpi, ohjauspistettä siirretään kohtisuoraan sivulle: kokeillaan
  // kasvavia taivutuksia vuorotellen kumpaankin suuntaan ja valitaan
  // pienin, joka kiertää kaikki esteet. Jos symmetrinen taivutus ei riitä
  // (este on lähellä toista päätä), ohjauspistettä siirretään myös rungon
  // suunnassa, jolloin kaari painottuu toiseen päähän. Ellei mikään kierrä
  // kaikkia, valitaan se, jossa esteisiin jää vähiten päällekkäisyyttä.
  function runko(p0, p1, esteet) {
    const keski = { x: (p0.x + p1.x) / 2, y: (p0.y + p1.y) / 2 };
    const dx = p1.x - p0.x;
    const dy = p1.y - p0.y;
    const pituus = Math.hypot(dx, dy) || 1;
    const nx = -dy / pituus;
    const ny = dx / pituus;
    const tx = dx / pituus;
    const ty = dy / pituus;
    let paras = keski;
    let parasPuute = Infinity;
    for (let askel = 0; askel <= 60; askel++) {
      for (const suunta of [0, 0.3, -0.3, 0.6, -0.6]) {
        const kx = keski.x + tx * suunta * pituus;
        const ky = keski.y + ty * suunta * pituus;
        for (const puoli of askel ? [1, -1] : [0]) {
          const siirto = puoli * askel * 40;
          const c = { x: kx + nx * siirto, y: ky + ny * siirto };
          const pahin = pahinEste(p0, c, p1, esteet);
          if (!pahin) return c;
          if (pahin.puute < parasPuute) {
            parasPuute = pahin.puute;
            paras = c;
          }
        }
      }
    }
    return paras;
  }

  function reitita(tilanne) {
    const { niput, taidot, nippuOf, sijainnit, yhteydet } = tilanne;
    const portit = new Map();
    const portti = (a, b) => {
      const avain = `${a}>${b}`;
      if (!portit.has(avain)) {
        const na = niput.get(a);
        const nb = niput.get(b);
        const d = Math.hypot(nb.x - na.x, nb.y - na.y) || 1;
        const r = na.radanSade + PORTTI;
        portit.set(avain, {
          x: na.x + (r * (nb.x - na.x)) / d,
          y: na.y + (r * (nb.y - na.y)) / d,
          ux: (nb.x - na.x) / d,
          uy: (nb.y - na.y) / d,
        });
      }
      return portit.get(avain);
    };

    // Rungot lasketaan kerran nippuparia kohti, jotta kaikki saman parin
    // yhteydet kulkevat täsmälleen samaa reittiä.
    const rungot = new Map();
    const rungonOhjaus = (a, b) => {
      const avain = a < b ? `${a}|${b}` : `${b}|${a}`;
      if (!rungot.has(avain)) {
        const [x, y] = a < b ? [a, b] : [b, a];
        const esteet = [...niput.values()].filter(
          (n) => n.id !== x && n.id !== y);
        rungot.set(avain, runko(portti(x, y), portti(y, x), esteet));
      }
      return rungot.get(avain);
    };

    const reitit = [];
    for (const t of taidot.values()) {
      for (const e of t.edellyttaa) {
        const na = nippuOf.get(e);
        const nb = nippuOf.get(t.id);
        const p = sijainnit.get(e);
        const q = sijainnit.get(t.id);
        if (na === nb) {
          const nippu = niput.get(na);
          const n = nippu.rata.length;
          const i = nippu.rata.indexOf(e);
          const j = nippu.rata.indexOf(t.id);
          let d;
          if (n > 2 && kehaEtaisyys(i, j, n) === 1) {
            const myota = (j - i + n) % n === 1 ? 1 : 0;
            const r = f1(nippu.radanSade);
            d = `M${f1(p.x)} ${f1(p.y)}A${r} ${r} 0 0 ${myota} ` +
              `${f1(q.x)} ${f1(q.y)}`;
          } else {
            d = `M${f1(p.x)} ${f1(p.y)}L${f1(q.x)} ${f1(q.y)}`;
          }
          reitit.push({ a: e, b: t.id, d, sisainen: true });
        } else {
          const pa = portti(na, nb);
          const pb = portti(nb, na);
          const ca = niput.get(na);
          const cb = niput.get(nb);
          const ohjaus = rungonOhjaus(na, nb);
          // Erkanemat suuntautuvat rungon alku- ja loppusuuntaan.
          const ta = Math.hypot(ohjaus.x - pa.x, ohjaus.y - pa.y) || 1;
          const tb = Math.hypot(ohjaus.x - pb.x, ohjaus.y - pb.y) || 1;
          pa.ux = (ohjaus.x - pa.x) / ta;
          pa.uy = (ohjaus.y - pa.y) / ta;
          pb.ux = (ohjaus.x - pb.x) / tb;
          pb.uy = (ohjaus.y - pb.y) / tb;
          // Erkanema taidosta porttiin kaartuu ensin säteen suuntaisesti
          // ulos radalta ja kääntyy sitten nipun suuntaan.
          const ra = Math.hypot(p.x - ca.x, p.y - ca.y) || 1;
          const rb = Math.hypot(q.x - cb.x, q.y - cb.y) || 1;
          const a1 = { x: p.x + (32 * (p.x - ca.x)) / ra,
            y: p.y + (32 * (p.y - ca.y)) / ra };
          const a2 = { x: pa.x - 30 * pa.ux, y: pa.y - 30 * pa.uy };
          const b2 = { x: pb.x - 30 * pb.ux, y: pb.y - 30 * pb.uy };
          const b1 = { x: q.x + (32 * (q.x - cb.x)) / rb,
            y: q.y + (32 * (q.y - cb.y)) / rb };
          const d = `M${f1(p.x)} ${f1(p.y)}` +
            `C${f1(a1.x)} ${f1(a1.y)} ${f1(a2.x)} ${f1(a2.y)} ` +
            `${f1(pa.x)} ${f1(pa.y)}` +
            `Q${f1(ohjaus.x)} ${f1(ohjaus.y)} ${f1(pb.x)} ${f1(pb.y)}` +
            `C${f1(b2.x)} ${f1(b2.y)} ${f1(b1.x)} ${f1(b1.y)} ` +
            `${f1(q.x)} ${f1(q.y)}`;
          reitit.push({ a: e, b: t.id, d, sisainen: false,
            nippu: na < nb ? `${na}|${nb}` : `${nb}|${na}` });
        }
      }
    }
    const nippureitit = yhteydet.map((y) => {
      const pa = portti(y.a, y.b);
      const pb = portti(y.b, y.a);
      const c = rungonOhjaus(y.a, y.b);
      return {
        avain: `${y.a}|${y.b}`, a: y.a, b: y.b, maara: y.maara,
        alku: { x: pa.x, y: pa.y }, ohjaus: c, loppu: { x: pb.x, y: pb.y },
        d: `M${f1(pa.x)} ${f1(pa.y)}Q${f1(c.x)} ${f1(c.y)} ` +
          `${f1(pb.x)} ${f1(pb.y)}`,
      };
    });
    return { reitit, nippureitit };
  }

  // ----------------------------------------------------------------
  // Julkinen rajapinta

  // Laskee koko asettelun. `aiempi` voi sisältää nippujen sijainnit, joista
  // jatketaan (esim. käyttäjän raahattua nippua); `kiinnitetyt` on joukko
  // nippuja, joita simulaatio ei siirrä.
  // Radan järjestys riippuu vain taitopuusta, joten se lasketaan kerran.
  const ratavalimuisti = new WeakMap();

  function laske(data, aiempi, kiinnitetyt) {
    const taidot = new Map(data.taidot.map((t) => [t.id, t]));
    const niput = muodostaNiput(data);
    if (!ratavalimuisti.has(data)) ratavalimuisti.set(data, new Map());
    const radat = ratavalimuisti.get(data);
    const nippuOf = new Map();
    for (const n of niput.values()) {
      for (const id of n.jasenet) nippuOf.set(id, n.id);
    }
    const nippulista = [...niput.values()];
    for (const n of nippulista) {
      if (!radat.has(n.id)) radat.set(n.id, jarjestaRata(n, taidot));
      n.rata = radat.get(n.id);
      const m = n.rata.length;
      n.radanSade = m === 1 ? 0 :
        Math.max(RATA_MIN, (m * SOLMUVALI) / (2 * Math.PI));
      n.sade = n.radanSade + REUNA;
      n.syvyys = Math.min(...n.jasenet.map((id) => taidot.get(id).taso)) - 1;
    }
    const keskus = nippulista[0].id;
    const yhteydet = nippujenYhteydet(niput, taidot, nippuOf);
    // Keskusnippu pysyy paikallaan, kunnes käyttäjä kiinnittää jonkin
    // nipun itse; silloin kartta saa asettua kiinnitetyn ympärille.
    const kiinni = kiinnitetyt && kiinnitetyt.size
      ? new Set(kiinnitetyt) : new Set([keskus]);

    if (aiempi) {
      for (const n of nippulista) {
        const p = aiempi.get(n.id);
        if (p) {
          n.x = p.x;
          n.y = p.y;
        }
      }
      simuloi(nippulista, yhteydet, 40, kiinni);
    } else {
      alkuasemat(nippulista, keskus);
      simuloi(nippulista, yhteydet, 900, kiinni);
    }
    kierraRadat(nippulista, taidot, nippuOf);

    const sijainnit = new Map();
    for (const n of nippulista) asetaSolmut(n, taidot, sijainnit);
    const { reitit, nippureitit } = reitita(
      { niput, taidot, nippuOf, sijainnit, yhteydet });
    return { niput, nippuOf, sijainnit, reitit, nippureitit, keskus };
  }

  vienti.TaitopuuAsettelu = { laske, solmunSade, bezier, VALI };
})(typeof module !== "undefined" ? module.exports : window);
