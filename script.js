/* ═══════════════════════════════════════════════════════════════
   Claude Code Plugins · interactions
   Scroll reveals · reading progress · active section · mobile menu
   ═══════════════════════════════════════════════════════════════ */
(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── 1. Scroll reveal ────────────────────────────────────── */
  const revealEls = document.querySelectorAll("[data-reveal]");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("in"));
  } else {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  /* ── 2. Top bar scrolled state + reading progress ────────── */
  const topbar = document.querySelector("[data-topbar]");
  const progress = document.querySelector("[data-progress]");
  let ticking = false;

  function onScroll() {
    const y = window.scrollY;
    const docH = document.documentElement.scrollHeight - window.innerHeight;
    const pct = docH > 0 ? (y / docH) * 100 : 0;

    if (topbar) topbar.toggleAttribute("data-scrolled", y > 24);
    if (progress) progress.style.setProperty("--p", pct.toFixed(2) + "%");
    ticking = false;
  }
  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(onScroll);
        ticking = true;
      }
    },
    { passive: true }
  );
  onScroll();

  /* ── 3. Active section → rail dots + top nav ─────────────── */
  const sections = document.querySelectorAll("[data-section]");
  const railLinks = document.querySelectorAll("[data-rail-dot]");
  const navLinks = document.querySelectorAll(".chapters a");

  function setActive(id) {
    railLinks.forEach((a) =>
      a.classList.toggle("is-active", a.dataset.railDot === id)
    );
    navLinks.forEach((a) =>
      a.classList.toggle("is-active", a.getAttribute("href") === "#" + id)
    );
  }

  if ("IntersectionObserver" in window && sections.length) {
    const so = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach((s) => so.observe(s));
  }

  /* ── 4. Mobile chapter menu ──────────────────────────────── */
  const menuBtn = document.querySelector("[data-menu-btn]");
  const menu = document.querySelector("[data-menu]");

  if (menuBtn && menu) {
    const close = () => {
      menu.removeAttribute("data-open");
      menuBtn.setAttribute("aria-expanded", "false");
    };
    menuBtn.addEventListener("click", () => {
      const open = menu.toggleAttribute("data-open");
      menuBtn.setAttribute("aria-expanded", String(open));
    });
    menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", close));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }

  /* ── 5. Subtle parallax on the floating hero blocks ──────── */
  if (!reduceMotion) {
    const blocks = document.querySelectorAll(".fb");
    const hero = document.querySelector(".hero");
    if (hero && blocks.length) {
      hero.addEventListener("mousemove", (e) => {
        const rx = (e.clientX / window.innerWidth - 0.5) * 2;
        const ry = (e.clientY / window.innerHeight - 0.5) * 2;
        blocks.forEach((b, i) => {
          const depth = ((i % 3) + 1) * 5;
          b.style.transform = `translate(${rx * depth}px, ${ry * depth}px)`;
        });
      });
      hero.addEventListener("mouseleave", () => {
        blocks.forEach((b) => (b.style.transform = ""));
      });
    }
  }
})();
