import { efekti, johdettu, signaali } from "./signaali.ts";

// @alku demo
const paikkoja = signaali(4);
const osallistujia = signaali(3);
const mahtuu = johdettu(() => osallistujia.get() <= paikkoja.get());

efekti(() => {
  console.log(`${osallistujia.get()}/${paikkoja.get()} mahtuu: ` +
    `${mahtuu.get() ? "kyllä" : "ei"}`);
});

osallistujia.set(5);   // efekti ajetaan uudelleen
paikkoja.set(8);
paikkoja.set(8);       // sama arvo: ei muutosta, ei ajoa
// @loppu demo
