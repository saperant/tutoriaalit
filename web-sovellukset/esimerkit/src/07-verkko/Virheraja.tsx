import { Component, type ErrorInfo, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  /** Virheen kirjaus, esimerkiksi virheenseurantapalveluun. */
  ilmoita?: (virhe: unknown, info: ErrorInfo) => void;
};

// @alku virheraja
/** Virheraja: jos jokin lapsista heittää poikkeuksen renderöinnissä,
 *  tilalle näytetään varanäkymä eikä koko sovellus katoa. Reactissa
 *  virheraja on yhä luokkakomponentti; hookia sille ei ole. */
export class Virheraja extends Component<Props, { kaatui: boolean }> {
  state = { kaatui: false };

  static getDerivedStateFromError() {
    return { kaatui: true };               // seuraava renderöinti: vara
  }

  componentDidCatch(virhe: unknown, info: ErrorInfo) {
    this.props.ilmoita?.(virhe, info);     // info.componentStack: missä
  }

  render() {
    if (!this.state.kaatui) return this.props.children;
    return (
      <div role="alert">
        <p>Näkymää ei voitu näyttää.</p>
        <button type="button"
                onClick={() => this.setState({ kaatui: false })}>
          Yritä uudelleen
        </button>
      </div>
    );
  }
}
// @loppu virheraja
