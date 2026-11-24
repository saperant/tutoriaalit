import { type ReactNode, useEffect, useRef } from "react";

// @alku sivu
/** Sivun runko. Reitin vaihtuessa ruudunlukija ei huomaa muutosta
 *  itsestään, joten otsikko saa fokuksen ja dokumentin nimi päivittyy. */
export function Sivu({ otsikko, children }: {
  otsikko: string;
  children: ReactNode;
}) {
  const h1 = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    document.title = `${otsikko} – Tilavaraus`;
    h1.current?.focus();
  }, [otsikko]);
  return (
    <>
      <h1 ref={h1} tabIndex={-1}>{otsikko}</h1>
      {children}
    </>
  );
}
// @loppu sivu
