/* Remarkable 2027 email banners: fills [data-copy="a.b"] elements (and [data-copy-label] aria-labels) from content/copy.json, then sets
   <html data-ready="true"> once fonts and images have loaded (the export script waits for it). */
const ROOT = "../../";

async function renderBanner() {
  const copy = await fetch(ROOT + "content/copy.json").then((r) => r.json());
  document.querySelectorAll("[data-copy]").forEach((el) => {
    const text = el.dataset.copy.split(".").reduce((o, k) => o[k], copy);
    // data-part="name" | "year" splits "Remarkable 2027" for the letter-spaced wordmark
    const [, name, year] = String(text).match(/^(.*?)\s*(\d{4})?$/);
    el.textContent = el.dataset.part === "name" ? name : el.dataset.part === "year" ? year : text;
  });
  document.querySelectorAll("[data-copy-label]").forEach((el) => {
    el.setAttribute("aria-label", el.dataset.copyLabel.split(".").reduce((o, k) => o[k], copy));
  });
  await document.fonts.ready;
  const imgs = [...document.images];
  await Promise.all(imgs.map((im) => (im.complete ? 0 : new Promise((r) => (im.onload = im.onerror = r)))));
  document.documentElement.dataset.broken = imgs.filter((im) => !im.naturalWidth).map((im) => im.getAttribute("src")).join(",");
  document.documentElement.dataset.ready = "true";
}

renderBanner();
