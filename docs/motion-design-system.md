# Portfolio Motion Design System

## Current-State Audit

The app runs on Streamlit 1.66.1 from `app.py`. Five sidebar routes render
Python component modules. The visual system is centralized in
`assets/styles/app.css`, with native Streamlit widgets and a small trusted
`st.html` fragment for portfolio tool chips. Before this motion pass, the app
had CSS hover transitions but no JavaScript, observers, animation runtime, or
third-party frontend component.

The strongest stable DOM hooks are project-owned `st-key-*` classes produced by
keyed Streamlit containers. A limited set of Streamlit `data-testid` hooks is
used for native widget internals such as buttons, metrics, images, alerts, and
the app viewport. Auto-generated `st-emotion-cache-*` classes are never used.

Streamlit route reruns and the Portfolio fragment can replace rendered DOM.
Motion therefore cannot assume that a node persists after an interaction.

## Motion Direction

The motion personality is premium editorial with a restrained mechanical edge.
Typography and structural rules lead. Images receive shallow physical depth.
Forms, long prose, charts, and tables stay calm so the authored moments retain
contrast.

The motion story follows anticipation, action, response, and settling:

- entrances begin close to their final position and decelerate into place;
- pointer interactions use very small depth and respond within one frame;
- pressed controls compress briefly and settle immediately;
- route and fragment replacements reveal the new context without delaying input.

## Technology Decision

The implementation uses Streamlit Custom Components v2 as one JavaScript-only
runtime. The installed API executes with normal app-page DOM privileges and
supports explicit cleanup. Native browser APIs provide the motion behavior:

- CSS custom properties and transitions for reusable tokens and states;
- `IntersectionObserver` for viewport entrances;
- `MutationObserver` for nodes recreated by Streamlit reruns;
- pointer events for desktop media depth;
- `requestAnimationFrame` for batched pointer and scroll writes;
- `matchMedia` for reduced-motion and input-capability adaptation.

GSAP, ScrollTrigger, Motion, and a Vite/TypeScript package are intentionally not
included. The app has no pinned sequence, scroll hijack, or multi-scene timeline
that needs those dependencies. Native APIs meet the required behavior with less
payload and a smaller cleanup surface. The View Transitions API is not used
because Streamlit owns route and fragment DOM replacement.

`requirements.txt` pins Streamlit 1.66.1 because the runtime depends on that
tested Custom Components v2 lifecycle and its rendered DOM contract.

## Motion Tokens

| Token | Value | Use |
| --- | ---: | --- |
| `duration-fast` | 120 ms | hover, press, selected state |
| `duration-medium` | 320 ms | controls, panels, metrics |
| `duration-slow` | 560 ms | hero and image reveals |
| `easing-standard` | `cubic-bezier(0.2, 0, 0, 1)` | direct interaction |
| `easing-emphasized` | `cubic-bezier(0.16, 1, 0.3, 1)` | entrances and settling |
| `reveal-distance` | 18 px | default spatial cue |
| `stagger-small` | 38–48 ms | navigation and chapters |
| `stagger-medium` | 55–70 ms | facts, metrics, panels |
| `pointer-tilt` | 1–2 degrees | desktop portrait and project media |
| `media-parallax` | 3–4 px | desktop image response |

## Section Motion Map

### Application shell

The sidebar identity and navigation enter once per browser runtime. Navigation
hover and selected states use a short horizontal response and a one-pixel accent
indicator. Route reruns do not intentionally replay the shell.

### About

The name uses the primary clipped heading reveal. Program and year follow as a
short stagger. The portrait reveals through a vertical mask and gains shallow
pointer depth on fine-pointer devices. The biography uses a quieter editorial
entrance.

### Autobiography

The page title and preface establish the reading context. Timeline chapters
alternate a small horizontal origin. A one-pixel accent line grows with native
scroll progress over the existing timeline rule. The code and download controls
enter as secondary panels.

### Skills

Controls establish first, followed by the two metrics. The chart and interactive
table reveal as complete surfaces; their internal Vega and dataframe DOM is not
manipulated.

### Portfolio

The group header, project index, and browsing toolbar establish hierarchy before
the selected project. Each project receives a unique keyed stage, so fragment
reruns animate only the replacement. Preview media gains restrained desktop tilt
and image parallax. Dialogs settle from a small scale and offset.

### Feedback

The heading and form enter as two calm beats. A newly created success or error
alert receives short feedback motion after the form rerun.

## Lifecycle and Selector Contract

The runtime follows `mount → discover → observe → animate → cleanup`.

1. The component registers once at module import and mounts immediately after
   the visual styles, before route content is emitted, to avoid reveal flicker.
2. Discovery adds `data-motion` attributes only to known semantic targets.
3. One intersection observer handles entrances.
4. One mutation observer discovers replacement nodes after route and fragment
   reruns.
5. Page-scoped reveal memory prevents unchanged content from replaying during a
   trivial widget rerun; project replacements, dialogs, and feedback can replay.
6. Pointer and scroll writes are batched through animation frames.
7. The returned component cleanup aborts listeners, disconnects observers,
   cancels pending frames, removes project-owned attributes, and restores inline
   properties.

Project-owned selectors are the primary contract:

- `st-key-about_*`
- `st-key-autobiography_*` and `st-key-autobio_chapter_*`
- `st-key-skills_*`
- `st-key-portfolio_page`, `st-key-pf_*`
- `st-key-feedback_*`
- `st-key-sidebar_identity`, `st-key-primary_navigation`

Streamlit hooks are limited to `stAppViewContainer`, `stButton`, `stLinkButton`,
`stDownloadButton`, `stMetric`, `stImage`, and `stAlert`.

## Responsive and Reduced Motion

Pointer tilt and parallax require a fine pointer, hover support, and a viewport
of at least 900 px. Touch and smaller layouts keep short entrance and press
feedback without perspective effects.

With `prefers-reduced-motion: reduce`, masks, translations, scale, perspective,
parallax, and scroll-linked progress are removed. Essential content remains
visible and a short opacity response preserves state feedback. Keyboard focus on
a pending target reveals it immediately.

## QA Requirements

Validate initial load, every sidebar route, Portfolio fragment switching,
Autobiography code execution, feedback validation and success, preview dialogs,
fast scrolling, reverse scrolling, resize, pointer enter/leave repetition,
keyboard focus, reduced motion, and component cleanup. No element may remain at
zero opacity if the JavaScript runtime fails.

## Implementation Plan and Status

- [x] Add the global motion tokens and progressive-enhancement foundation.
- [x] Mount one lifecycle-managed Custom Components v2 runtime.
- [x] Add semantic page, navigation, and project-stage wrappers.
- [x] Choreograph About and major page entrances.
- [x] Add Autobiography timeline progress and chapter sequencing.
- [x] Add Portfolio media depth and project replacement motion.
- [x] Add shared navigation, button, form, tab, and feedback microinteractions.
- [x] Add responsive pointer capability checks and reduced-motion behavior.
- [x] Verify reruns, interactions, cleanup structure, syntax, dependencies, and tests.
