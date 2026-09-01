# Elemental Forge — 2D Procedural Game Engine Studio

A browser-based 2D game-dev studio that generates and randomizes pixel-art tilemaps, prop sprites, and item cards across four elemental aspects (Water, Fire, Air, Earth), with a playable sandbox and real export formats. No backend — everything runs client-side and is fully deterministic from a seed.

The boa-bigapi-framework repo is used as naming/architecture inspiration only (modular generator registry, seeded pipelines) — no dependency, no API calls.

## Look and feel

Pixel-art first: crisp 16px tiles rendered on canvas with nearest-neighbor scaling, a retro editor chrome around them (dark panel UI, monospace/pixel type, elemental accent colors — seafoam, ember, pale wind-gold, moss-clay). Item cards borrow the codex framing from the reference plate but rendered as pixel panels, not parchment photography.

## Pages

1. **/** — Studio. The main surface: seed bar, element selector, live tilemap canvas, and a right-hand inspector with generation parameters.
2. **/sandbox** — Playable scene. Drops a controllable sprite onto the current generated map with collision, tile-driven movement, and simple element interactions.
3. **/library** — Session gallery of everything generated this session (maps, props, cards) with re-roll and export.
4. **/codex** — Item card generator: randomized elemental artifacts with stat blocks in the reference style.

## Generation engine

Core is a small deterministic engine in `src/engine/`:

- **RNG** — seeded mulberry32 + hashed string seeds, so the same seed always reproduces the same world.
- **Noise** — value/simplex-style fBm for terrain height, moisture, and flow fields.
- **Biome rules per element**
  - Water: archipelagos, currents, tide shelves, coral shallows
  - Fire: obsidian plateaus, lava veins, ash flats, ember vents
  - Air: sky islands, cloud shelves, gust corridors, void gaps
  - Earth: cavern systems, cliffs, ore seams, forest mantles
- **Tilemap builder** — height/moisture → tile IDs, autotiling for edges/transitions, prop scatter with Poisson-ish spacing, walkability mask for the sandbox.
- **Sprite generator** — procedural pixel props (crystals, vents, rocks, plants, artifacts) drawn to offscreen canvases with per-element palettes and mirrored symmetry.
- **Tileset generator** — palettes + per-tile pixel routines so tiles are generated too, not shipped as static art.
- **Item generator** — randomized name, type, dimensions, composition, properties, dispersion/resonance stats, rendered as a pixel codex card.

## Studio controls

Seed (editable + randomize), element aspect, map size, land/water threshold, roughness, prop density, palette variant, tile size, and grid/collision overlay toggles. Every control re-derives the world instantly from the seed.

## Sandbox

Canvas game loop with fixed timestep, WASD/arrow movement, collision against the walkability mask, camera follow, and element flavor: water slows, fire damages/glows, air gives dash lift, earth blocks. Pause/reset, and it always plays the map currently in the studio.

## Exports

- **PNG** — rendered map, individual sprite sheets, and item cards.
- **JSON** — Tiled-compatible tilemap (orthogonal, embedded layer data, tileset metadata) plus a raw engine JSON with the seed and full parameter set so any generation is reproducible.

## Technical notes

- TanStack Start routes: `src/routes/index.tsx` (studio, replacing the placeholder), `/sandbox`, `/library`, `/codex`.
- Engine is pure TS with no DOM at module scope; canvas rendering lives in `useEffect`/refs so SSR stays clean.
- Generated state is held in a shared store (React context + reducer) keyed by seed; library persists in-memory for the session (localStorage read only after hydration).
- Design tokens added to `src/styles.css` as semantic oklch variables (element accents, panel surfaces) — no hardcoded color utilities.
- Per-route `head()` metadata with unique titles/descriptions.
- No Lovable Cloud in this version; accounts and a persistent saved library can be added later.
