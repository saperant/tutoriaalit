import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Testing Library siivoaa renderöidyt komponentit automaattisesti vain,
// jos testikehyksen globaalit funktiot ovat käytössä. Vitestissä ne
// eivät ole oletuksena, joten siivous kytketään tässä.
afterEach(() => cleanup());
