import { expect, test } from "vitest";
import { type Hakuehdot, kuunteleHakua } from "./lomake.ts";

test("submit lukee ehdot ja estää sivun latauksen", () => {
  document.body.innerHTML = `
    <form>
      <label>Paikkoja vähintään
        <input name="vahintaan" type="number" min="1" value="6"></label>
      <label>Varuste
        <select name="varuste">
          <option value="">kaikki</option>
          <option selected>näyttö</option>
        </select></label>
      <button>Hae</button>
    </form>`;
  const lomake = document.querySelector("form")!;
  const haut: Hakuehdot[] = [];
  kuunteleHakua(lomake, (ehdot) => haut.push(ehdot));
  const tapahtuma = new Event("submit", { cancelable: true });
  lomake.dispatchEvent(tapahtuma);
  expect(tapahtuma.defaultPrevented).toBe(true);
  expect(haut).toEqual([{ vahintaan: 6, varuste: "näyttö" }]);
});
