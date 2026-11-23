// strict-tila sisältää noImplicitAny-tarkistuksen.
function alv(hinta) { return hinta * 0.255; } // @virhe: hinta on any

function arvonlisavero(hinta: number): number {
  return hinta * 0.255; // yleinen verokanta 25,5 %
}
console.log(arvonlisavero(100).toFixed(2));
