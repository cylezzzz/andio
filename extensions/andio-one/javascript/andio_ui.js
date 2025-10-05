// ANDIO One – UI Helpers for A1111 extension
// Path: extensions/andio-one/javascript/andio_ui.js

document.title = "ANDIO One – Wardrobe Editor";
const favicon = document.createElement("link");
favicon.rel = "icon";
favicon.href = "extensions/andio-one/assets/logo.png";
document.head.appendChild(favicon);

(function () {
  console.log("[ANDIO] UI loaded");

  // Wait until our tab exists
  function ready(selector, cb) {
    const el = document.querySelector(selector);
    if (el) return cb(el);
    const obs = new MutationObserver(() => {
      const el2 = document.querySelector(selector);
      if (el2) {
        obs.disconnect();
        cb(el2);
      }
    });
    obs.observe(document.documentElement, { childList: true, subtree: true });
  }

  // Small helpers
  const ls = {
    get(k, d = "") { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch {} },
    del(k) { try { localStorage.removeItem(k); } catch {} }
  };

  // Persist a textbox by label text (works for ANDIO P1–P5/Negative/Seed)
  function bindPersistByLabel(labelText, key) {
    const allLabels = Array.from(document.querySelectorAll('#andio_root label'));
    const label = allLabels.find(l => (l.textContent || "").trim() === labelText);
    if (!label) return;
    const input = label.parentElement?.querySelector("textarea, input");
    if (!input) return;

    // init value
    const saved = ls.get(key, "");
    if (saved && !input.value) input.value = saved;

    input.addEventListener("input", () => ls.set(key, input.value));
  }

  // Randomize seed button (⌘/Ctrl + R)
  function addSeedRandomizer() {
    const allLabels = Array.from(document.querySelectorAll('#andio_root label'));
    const seedLbl = allLabels.find(l => (l.textContent || "").trim() === "Seed");
    const seedInput = seedLbl?.parentElement?.querySelector("input, textarea");
    if (!seedInput) return;

    const btn = document.createElement("button");
    btn.className = "gr-button";
    btn.style.marginLeft = "8px";
    btn.textContent = "🎲";
    btn.title = "Random Seed (Ctrl/Cmd + R)";
    seedLbl.parentElement.appendChild(btn);

    function rnd() {
      seedInput.value = (Math.floor(Math.random() * 2_147_483_647)).toString();
      seedInput.dispatchEvent(new Event("input", { bubbles: true }));
    }
    btn.addEventListener("click", rnd);

    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "r") {
        e.preventDefault();
        rnd();
      }
    });
  }

  // Ctrl/Cmd + Enter → Generate
  function addGenerateShortcut() {
    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "enter") {
        const btns = Array.from(document.querySelectorAll("#andio_root button"));
        const run = btns.find(b => /Generate/i.test(b.textContent || ""));
        if (run) { e.preventDefault(); run.click(); }
      }
    });
  }

  // Drag & drop image into the left image input
  function enableDragDrop() {
    const imgs = document.querySelectorAll("#andio_root .gr-image input[type='file']");
    if (!imgs.length) return;
    imgs.forEach((input) => {
      const wrap = input.closest(".gr-image");
      if (!wrap) return;

      ["dragenter", "dragover"].forEach(t =>
        wrap.addEventListener(t, (ev) => { ev.preventDefault(); wrap.style.outline = "2px dashed #e40a2d88"; })
      );
      ["dragleave", "drop"].forEach(t =>
        wrap.addEventListener(t, (ev) => { ev.preventDefault(); wrap.style.outline = ""; })
      );
      wrap.addEventListener("drop", (ev) => {
        const file = ev.dataTransfer?.files?.[0];
        if (file) {
          const dt = new DataTransfer();
          dt.items.add(file);
          input.files = dt.files;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
    });
  }

  // Persist core inputs
  function bindPersistence() {
    bindPersistByLabel("P1", "andio_p1");
    bindPersistByLabel("P2", "andio_p2");
    bindPersistByLabel("P3", "andio_p3");
    bindPersistByLabel("P4", "andio_p4");
    bindPersistByLabel("P5", "andio_p5");
    bindPersistByLabel("Negative Prompt", "andio_negative");
    bindPersistByLabel("Seed", "andio_seed");
  }

  // Tiny status ping (optional visual cue in console)
  function pingA1111() {
    fetch("/sdapi/v1/system-info").then(r => r.json()).then(j => {
      console.log("[ANDIO] A1111 OK:", j?.cuda?.version ?? "n/a");
    }).catch(() => console.warn("[ANDIO] A1111 system-info not reachable"));
  }

  // Initialize when our root is ready
  ready("#andio_root", () => {
    addGenerateShortcut();
    addSeedRandomizer();
    enableDragDrop();
    bindPersistence();
    setTimeout(pingA1111, 1000);
  });
})();
