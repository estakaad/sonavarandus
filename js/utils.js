/**
 * wordLink(w, className)
 * Loob <a> elemendi sõnale, mis lingivad sõnaveebi.
 *
 * @param {string} w - sõna
 * @param {string} [className] - valikuline CSS klass
 * @returns {HTMLAnchorElement}
 */
function wordLink(w, className) {
  const a = document.createElement("a");
  a.href = `https://sonaveeb.ee/search/unif/dlall/dsall/${encodeURIComponent(w)}/1/est`;
  a.target = "_blank";
  a.rel = "noopener";
  a.textContent = w;
  if (className) a.className = className;
  return a;
}
