# Frontend Changes

## Dark/Light Mode Toggle

### Features added
- **Light theme CSS variables** — full color palette for light mode
- **Theme toggle button** — fixed top-right, sun/moon icon, smooth animated transition
- **Preference persistence** — user's choice saved to `localStorage`

---

### `frontend/style.css`

**Light theme variables** added as `[data-theme="light"]` block immediately after `:root`:

| Variable | Dark | Light |
|---|---|---|
| `--background` | `#0f172a` | `#f8fafc` |
| `--surface` | `#1e293b` | `#ffffff` |
| `--surface-hover` | `#334155` | `#f1f5f9` |
| `--text-primary` | `#f1f5f9` | `#0f172a` |
| `--text-secondary` | `#94a3b8` | `#64748b` |
| `--border-color` | `#334155` | `#e2e8f0` |
| `--assistant-message` | `#374151` | `#f1f5f9` |
| `--shadow` | `rgba(0,0,0,0.3)` | `rgba(0,0,0,0.1)` |
| `--welcome-bg` | `#1e3a5f` | `#eff6ff` |
| `--focus-ring` | `rgba(37,99,235,0.2)` | `rgba(37,99,235,0.15)` |

Primary/hover/user-message colors unchanged (blue works on both themes).

**Theme transition** — smooth 0.3s ease transition on `background-color`, `color`, and `border-color` for body, sidebar, chat area, input, and message elements.

**Toggle button styles** (`.theme-toggle`):
- `position: fixed; top: 1rem; right: 1rem; z-index: 100`
- 40×40px circular button, matches surface/border colors
- Hover: primary color border + subtle lift
- Focus: 3px focus ring (keyboard accessible)
- Moon/sun SVGs animate via `opacity` + `transform` (rotate/scale) on 0.3s ease
- Dark mode shows moon; light mode shows sun

**Light theme scrollbar and code block** overrides added.

---

### `frontend/index.html`

- Added `<button class="theme-toggle" id="themeToggle">` before the `<script>` tags
- Contains two inline SVGs: `.icon-moon` (crescent) and `.icon-sun` (circle + rays)
- `aria-label="Switch to light mode"` (updated dynamically by JS)
- `aria-hidden="true"` on both SVGs (label is on the button itself)

---

### `frontend/script.js`

- Added `themeToggle` to DOM element declarations
- `initTheme()` — reads `localStorage` on load, applies saved theme and correct aria-label
- `toggleTheme()` — flips `data-theme` attribute on `<html>`, updates `localStorage` and aria-label
- `themeToggle.addEventListener('click', toggleTheme)` wired in `setupEventListeners()`
