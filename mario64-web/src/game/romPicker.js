// Shared "choose your ROM" gate. The ROM never leaves the browser; we optionally keep a
// copy in IndexedDB so returning players don't have to pick it again.
import { loadRom } from '../rom/rom.js';

const DB = 'mario64-web';
const STORE = 'rom';

function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function cacheRom(bytes) {
  try {
    const db = await openDb();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, 'readwrite');
      tx.objectStore(STORE).put(bytes, 'sm64');
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error);
    });
  } catch { /* storage unavailable: just ask again next time */ }
}

async function cachedRom() {
  try {
    const db = await openDb();
    return await new Promise((resolve) => {
      const req = db.transaction(STORE).objectStore(STORE).get('sm64');
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => resolve(null);
    });
  } catch {
    return null;
  }
}

export async function forgetRom() {
  try {
    const db = await openDb();
    db.transaction(STORE, 'readwrite').objectStore(STORE).delete('sm64');
  } catch { /* nothing cached */ }
}

/**
 * Show the ROM gate until a valid ROM is chosen, then call onRom(rom).
 */
export async function pickRomFile(onRom) {
  const gate = document.getElementById('romGate');
  const input = document.getElementById('romFile');
  const error = document.getElementById('romError');

  const accept = async (bytes, remember) => {
    const rom = await loadRom(bytes);
    if (remember) cacheRom(rom.bytes);
    gate.hidden = true;
    await onRom(rom);
  };

  const cached = await cachedRom();
  if (cached) {
    try {
      await accept(new Uint8Array(cached), false);
      return;
    } catch (e) {
      console.warn('Cached ROM rejected', e);
      forgetRom();
    }
  }

  const handle = async (file) => {
    error.textContent = '';
    try {
      await accept(new Uint8Array(await file.arrayBuffer()), true);
    } catch (e) {
      console.error(e);
      error.textContent = e.message;
      gate.hidden = false;
    }
  };
  input.addEventListener('change', () => input.files[0] && handle(input.files[0]));
  gate.addEventListener('dragover', (e) => { e.preventDefault(); gate.classList.add('drag'); });
  gate.addEventListener('dragleave', () => gate.classList.remove('drag'));
  gate.addEventListener('drop', (e) => {
    e.preventDefault();
    gate.classList.remove('drag');
    if (e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]);
  });
  gate.hidden = false;
}
