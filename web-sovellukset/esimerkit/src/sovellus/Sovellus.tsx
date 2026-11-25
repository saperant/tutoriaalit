import { lazy, type ReactNode, Suspense } from "react";
import { VarausLomake } from "../05-lomakkeet/VarausLomake.tsx";
import { TilaHaku } from "../04-react/TilaHaku.tsx";
import type { Asiakas } from "../07-verkko/asiakas.ts";
import { type Haku, useHaku } from "../07-verkko/useHaku.ts";
import { Virheraja } from "../07-verkko/Virheraja.tsx";
import {
  Linkki, siirry, sovita, useSijainti,
} from "../08-reititys/reititin.tsx";
import { Sivu } from "./Sivu.tsx";

// Harvoin käytetty näkymä ladataan vasta tarvittaessa (koodin pilkkominen).
const Raportti = lazy(() => import("./Raportti.tsx"));

// @alku sovellus
export function Sovellus({ api, tanaan }: { api: Asiakas; tanaan: string }) {
  const { pathname } = useSijainti();
  const tila = sovita("/tilat/:id", pathname);

  let sisalto;
  if (pathname === "/") sisalto = <TilatSivu api={api} />;
  else if (tila?.id) {
    sisalto = <TilaSivu key={tila.id} id={tila.id} api={api}
                        tanaan={tanaan} />;
  } else if (pathname === "/raportti") {
    sisalto = (
      <Suspense fallback={<p>Ladataan…</p>}>
        <Raportti api={api} />
      </Suspense>);
  } else {
    sisalto = <Sivu otsikko="Sivua ei löydy"><p>Tarkista osoite.</p></Sivu>;
  }

  return (
    <>
      <header>
        <nav aria-label="Päävalikko">
          <Linkki to="/">Tilat</Linkki>{" "}
          <Linkki to="/raportti">Raportti</Linkki>
        </nav>
      </header>
      <main>
        <Virheraja key={pathname}>{sisalto}</Virheraja>
      </main>
    </>
  );
}
// @loppu sovellus

// @alku sivut
function TilatSivu({ api }: { api: Asiakas }) {
  const haku = useHaku("tilat", (signal) => api.haeTilat(signal));
  return (
    <Sivu otsikko="Kokoustilat">
      <Tila haku={haku}>
        {(tilat) => <TilaHaku tilat={tilat}
                              onVaraa={(id) => siirry(`/tilat/${id}`)} />}
      </Tila>
    </Sivu>
  );
}

function TilaSivu({ id, api, tanaan }: {
  id: string; api: Asiakas; tanaan: string;
}) {
  const haku = useHaku(id, (signal) => api.haeTila(id, signal));
  return (
    <Sivu otsikko={haku.tila === "valmis" ? haku.data.nimi : "Tila"}>
      <Tila haku={haku}>
        {(t) => (<>
          <p>{t.kerros}. krs, {t.paikkoja} paikkaa</p>
          <VarausLomake tilaId={t.id} tanaan={tanaan} laheta={api.varaa} />
        </>)}
      </Tila>
    </Sivu>
  );
}

/** Lataus-, virhe- ja valmis-tila samalla tavalla joka näkymässä. */
function Tila<T>({ haku, children }: {
  haku: Haku<T> & { yritaUudelleen: () => void };
  children: (data: T) => ReactNode;
}) {
  if (haku.tila === "ladataan") return <p role="status">Ladataan…</p>;
  if (haku.tila === "virhe") {
    return (
      <div role="alert">
        <p>Tietojen haku epäonnistui: {haku.virhe.message}</p>
        <button type="button" onClick={haku.yritaUudelleen}>
          Yritä uudelleen
        </button>
      </div>);
  }
  return <>{children(haku.data)}</>;
}
// @loppu sivut
