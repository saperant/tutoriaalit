import { render } from "@testing-library/react";
import { expect, test } from "vitest";
import { Kuvaus, VaarallinenKuvaus } from "./Kuvaus.tsx";

const HYOKKAYS = 'Hyvä tila *heti* <img src=x onerror="alert(1)">';

// @alku testi
test("muotoilu toimii eikä HTML:ää synny", () => {
  const { container } = render(<Kuvaus teksti={HYOKKAYS} />);
  expect(container.querySelector("em")?.textContent).toBe("heti");
  expect(container.querySelector("img")).toBeNull();
  expect(container.textContent).toContain("<img src=x");
});

test("dangerouslySetInnerHTML päästää elementin läpi", () => {
  const { container } = render(<VaarallinenKuvaus teksti={HYOKKAYS} />);
  expect(container.querySelector("img[onerror]")).not.toBeNull();
});
// @loppu testi
