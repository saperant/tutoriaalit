import type { ReactNode } from "react";

// @alku kuvaus
/** Näyttää käyttäjän kirjoittaman kuvauksen, jossa *tähdet* korostavat
 *  ja tyhjä rivi aloittaa kappaleen. Muotoilu jäsennetään React-
 *  elementeiksi; HTML:ää ei synny, joten syötteestä ei voi tulla skriptiä. */
export function Kuvaus({ teksti }: { teksti: string }) {
  return (
    <>
      {teksti.split(/\n{2,}/).map((kappale, i) => (
        <p key={i}>{korosta(kappale)}</p>     // kappaleet eivät järjesty
      ))}
    </>
  );
}

function korosta(teksti: string): ReactNode[] {
  return teksti.split(/(\*[^*\n]+\*)/).map((osa, i) =>
    osa.startsWith("*") && osa.endsWith("*") && osa.length > 2
      ? <em key={i}>{osa.slice(1, -1)}</em>
      : osa);
}
// @loppu kuvaus

// @alku vaarallinen
/** VÄÄRIN: sama muotoilu merkkijonona innerHTML:ään. Syötteen HTML
 *  päätyy sivulle sellaisenaan. */
export function VaarallinenKuvaus({ teksti }: { teksti: string }) {
  const html = teksti.replace(/\*([^*\n]+)\*/g, "<em>$1</em>");
  return <p dangerouslySetInnerHTML={{ __html: html }} />;
}
// @loppu vaarallinen
