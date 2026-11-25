import { bootstrapApplication } from "@angular/platform-browser";
import { Sovellus } from "./app/sovellus";

bootstrapApplication(Sovellus).catch((virhe: unknown) => {
  console.error(virhe);
});
