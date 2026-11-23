/**
 * @param {string} kentta  lomakkeelta luettu arvo, esim. "5"
 * @returns {number}
 */
function tuplaa(kentta) {
  const maara = Number(kentta);
  if (Number.isNaN(maara)) {
    throw new RangeError(`ei luku: ${kentta}`);
  }
  return kentta * 2; // @virhe
  return maara * 2;
}

console.log(tuplaa("5"));
