---
name: Restorative Companion
colors:
  surface: '#fbf9f6'
  surface-dim: '#dbdad7'
  surface-bright: '#fbf9f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f0'
  surface-container: '#efeeeb'
  surface-container-high: '#eae8e5'
  surface-container-highest: '#e4e2df'
  on-surface: '#1b1c1a'
  on-surface-variant: '#414844'
  inverse-surface: '#30312f'
  inverse-on-surface: '#f2f0ed'
  outline: '#727974'
  outline-variant: '#c1c8c3'
  surface-tint: '#446557'
  primary: '#325346'
  on-primary: '#ffffff'
  primary-container: '#4a6b5d'
  on-primary-container: '#c6ead8'
  inverse-primary: '#abcebe'
  secondary: '#625a7b'
  on-secondary: '#ffffff'
  secondary-container: '#e2d7ff'
  on-secondary-container: '#645c7e'
  tertiary: '#66452a'
  on-tertiary: '#ffffff'
  tertiary-container: '#805d3f'
  on-tertiary-container: '#ffdbc0'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#c6ebd9'
  primary-fixed-dim: '#abcebe'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#2d4d40'
  secondary-fixed: '#e8ddff'
  secondary-fixed-dim: '#ccc1e8'
  on-secondary-fixed: '#1e1734'
  on-secondary-fixed-variant: '#4a4262'
  tertiary-fixed: '#ffdcc2'
  tertiary-fixed-dim: '#ebbe9a'
  on-tertiary-fixed: '#2d1601'
  on-tertiary-fixed-variant: '#5f4024'
  background: '#fbf9f6'
  on-background: '#1b1c1a'
  surface-variant: '#e4e2df'
typography:
  display:
    fontFamily: Quicksand
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 52px
    letterSpacing: -0.02em
  display-mobile:
    fontFamily: Quicksand
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Quicksand
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Quicksand
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Quicksand
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
  headline-sm:
    fontFamily: Quicksand
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Nunito Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Nunito Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Nunito Sans
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Quicksand
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Quicksand
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Quicksand
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.04em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 1rem
  margin: 3rem
  margin-mobile: 1.25rem
  space-xs: 0.375rem
  space-sm: 0.75rem
  space-md: 1.25rem
  space-lg: 2rem
  space-xl: 3.5rem
---

## Brand & Style

This design system embodies an anti-anxiety, restorative sanctuary engineered specifically for overwhelmed college students facing cognitive overload, burnout, and executive dysfunction. The emotional signature is akin to stepping into a quiet, sunlit room with a warm mug of herbal tea: grounded, safe, unhurried, and devoid of judgment.

The visual aesthetic synthesizes **Soft Minimalist Warmth** with **Organic Tactility**. Unlike conventional productivity suites that rely on urgency triggers—such as ticking timers, punitive red badges, and guilt-inducing streaks—this interface operates on restorative reassurance. Visual clutter is stripped away to leave generous atmospheric white space, soft earth-tinted surfaces, and pillowy, organic containers that soothe sensory tension.

Every visual interaction should deliver emotional decompression:
- **Pacing**: Deliberate, calm micro-interactions and transitions with soft physics (gentle spring curves, never snappy or jarring).
- **Tone**: Grounded companionship. Information architecture surfaces only one actionable prompt at a time ("What feels doable right now?"), dismantling paralysis through sensory comfort.

## Colors

The palette draws directly from botanical and earthy minerals, engineered strictly to mitigate blue-light fatigue and sensory irritation. The interface avoids pure stark blacks (#000000) and harsh clinical whites (#FFFFFF).

### Color Hierarchy & Roles
- **Primary (`#4A6B5D` Sage Forest)**: The stabilizing core. Applied to primary completion affordances, active navigational markers, and focused elements. Supported by:
  - *Sage Wash (`#E8EFEA`)*: Quiet container fill for primary groupings and gentle active states.
  - *Sage Muted (`#8FA89B`)*: Secondary borders, non-urgent indicators, and illustrative accents.
- **Secondary (`#7B7295` Dusky Lavender)**: The introspective accent. Used for reflection tools, breathing prompts, gentle audio anchors, and mindful categorization. Supported by:
  - *Lavender Wash (`#F3F0F8`)*: Ambient tinted backdrops and contemplative cards.
  - *Lavender Soft (`#D8D2E7`)*: Subtle highlight fills and chip strokes.
- **Tertiary (`#C49A78` Warm Ochre)**: Gentle grounding energy. Reserved for delicate affirmation moments, progress milestones, and soft focus transitions.
- **Neutral Canvas (`#FAF8F5` Steamed Cream)**: The dominant application canvas, supported by:
  - *Surface Elevated (`#FFFDFB` Soft Milk)*: Pure resting surface for elevated cards and modals.
  - *Surface Subdued (`#F5F1EB` Oatmeal Linen)*: Secondary grouped wells and inactive toggles.
- **Typography Neutrals**:
  - *Charcoal Primary (`#2D3436` Deep Slate)*: Soft, high-legibility text without cold stark contrast.
  - *Slate Secondary (`#4A5568` Weathered Bark)*: Supporting guidance, timestamps, and low-priority metadata.

### Non-Judgmental Alert Model
Never use aggressive reds, alarming ambers, or vibration-inducing yellows. For notices requiring user attention, use a warm apricot tint (`#E0876A` at 10% opacity for backgrounds, solid for icons) framed with soft language.

## Typography

The typographic hierarchy pairs **Quicksand** (for headings, callouts, and tactile labels) with **Nunito Sans** (for body copy, reflective journals, and instructional prompts). 

- **Quicksand** imparts an organic, rounded terminal structure that softens hard cognitive edges, avoiding cold corporate rigidity while remaining structurally sound.
- **Nunito Sans** provides open counters, balanced x-height, and superior legibility for longer reading intervals without straining fatigued eyes.

### Typographic Intent
- Never use all-caps transformations for body or alerts; all-caps is restricted exclusively to tiny micro-labels (`label-sm`) with wide tracking to prevent visual shouting.
- Paragraphs must maintain generous line-heights (1.5–1.6) to reduce visual crowding for readers experiencing cognitive strain or ADHD paralysis.

## Layout & Spacing

The layout philosophy uses a **Centered Focus Well** within a flexible, calm grid structure. Rather than packing density across multiple concurrent panes, screens are intentionally constrained to create visual quietude.

### Grid & Composition
- **Desktop (≥1024px)**: Single-column core reading/focus well capped at `680px` maximum width for focus modes, or an 8-column layout capped at `960px` for multi-item dashboards. Generous outer margins (`margin`: 3rem) ensure breathing space.
- **Tablet (768px – 1023px)**: 6-column layout with 2rem side padding and 1.25rem gutters.
- **Mobile (≤767px)**: Fluid single-column with `margin-mobile` (1.25rem). Layout structures stack vertically with stacked tactile pill cards.

### Spacing Rhythm
Spacing is intentional empty air. Gaps between distinct thematic sections prioritize `space-xl` (3.5rem) to ensure clear cognitive segregation. Micro-spacing within elements relies on soft multiples of 6px/12px to complement rounded geometries.

## Elevation & Depth

Visual hierarchy uses a **Warm Tonal Layering** system bolstered by **Atmospheric Diffused Shadows**. Heavy, high-contrast drop shadows are strictly avoided. Depth feels like soft, layered paper or tactile linen stationery.

### Surface Tiers
- **Tier 0 (Backdrop)**: `#FAF8F5` (Steamed Cream canvas).
- **Tier 1 (Resting Cards & Pillows)**: `#FFFDFB` (Soft Milk) backed by an extra-diffuse ambient shadow: `0 8px 32px -4px rgba(74, 107, 93, 0.05), 0 2px 8px -2px rgba(45, 52, 54, 0.03)`.
- **Tier 2 (Interactive Floating Surfaces & Sheets)**: `#FFFFFF` with a calm, comforting lift: `0 16px 40px -8px rgba(123, 114, 149, 0.08), 0 4px 12px -2px rgba(45, 52, 54, 0.02)`.
- **Tier 3 (Active Focus Overlays & Modals)**: `#FFFDFB` suspended over a semi-transparent warm backdrop blur (`rgba(250, 248, 245, 0.85)` with `backdrop-filter: blur(12px)`).

### Outlines & Borders
Surfaces rely primarily on tone shifts, accompanied by a hairline, whisper-soft border: `1px solid rgba(74, 107, 93, 0.08)`. This defines card architecture without creating rigid cages.

## Shapes

The design system employs **Pill-Shaped & Pillowy Organic Contours** (Level 3). Sharp edges and razor corners induce subtle subconscious tension; hyper-soft rounded corners feel tactile, safe, and welcoming.

### Corner Radius Implementation
- **Full Pills (`rounded-full` / 9999px)**: Applied to all primary buttons, interactive chips, tag indicators, and floating navigation bars.
- **Large Cards & Panels (`rounded-3xl` / 2rem / 32px)**: Primary focus modules, daily check-in containers, and modal sheets.
- **Medium Elements (`rounded-2xl` / 1.25rem / 20px)**: Input fields, sub-cards, dropdown menus, and list items.
- **Inner Controls (`rounded-xl` / 0.75rem / 12px)**: Checkboxes, nested toggles, and small badges.

## Components

### Buttons
- **Primary ("Gentle Focus")**: Pill-shaped (`rounded-full`), background `#4A6B5D`, text `#FFFDFB`, padding `14px 28px`. Hover introduces a smooth micro-lift (`translate-y(-1px)`) and background shift to `#3D594D`, never an abrupt color invert. Shadow: `0 6px 20px -2px rgba(74, 107, 93, 0.25)`.
- **Secondary ("Quiet Step")**: Background `#E8EFEA`, text `#4A6B5D`, border `1px solid transparent`. Hover transitions to `#D8E4DC`.
- **Tertiary / Ghost ("Soft Echo")**: Background transparent, text `#7B7295`. Hover adds `#F3F0F8` background tint.

### Pill Chips & Tags
- Interactive filters and emotional state markers feature full pill radius with generous vertical padding (`8px 16px`).
- Inactive state: `#F5F1EB` background with `#4A5568` text.
- Active state: `#E8EFEA` background with `#4A6B5D` text and a subtle 1.5px border `#8FA89B`.

### Lists & Single Task Cards
- Instead of crowded checkbox rows, tasks are presented as **Comfort Tiles** with `rounded-2xl`, `#FFFDFB` background, and `20px` internal padding.
- List items feature generous spacing gaps (`space-sm`).
- Completed items do not use aggressive red or harsh strike-throughs; they fade softly to 45% opacity with an animated floral checkmark icon.

### Selection Controls (Checkboxes & Radios)
- **Checkboxes**: Sized at `24px × 24px` with a soft `rounded-lg` (8px). Inactive state is a gentle border `2px solid #8FA89B` with `#FAF8F5` fill. Checked state fills with `#4A6B5D` showing a smooth, hand-drawn check in `#FFFDFB`.
- **Radio Buttons**: Concentric rounded circles (`24px`), filling inwards with a warm `#7B7295` dot.

### Input Fields
- Enclosed in pillowy `rounded-2xl` boundaries, with `#FFFDFB` background, `16px 20px` padding, and border `1.5px solid rgba(74, 107, 93, 0.12)`.
- Focus state gently illuminates the border to `#8FA89B` with an ambient glow: `0 0 0 4px rgba(143, 168, 155, 0.18)`. No harsh primary outline.
- Placeholder text uses reassuring, non-judgmental prompts: *"Jot down whatever comes to mind..."* or *"One small thing you can touch..."*.

### Cards & Focus Containers
- Resting surface `#FFFDFB`, radius `32px` (`rounded-3xl`), border `1px solid rgba(74, 107, 93, 0.06)`. Internal padding scales from `space-md` on mobile to `space-lg` on desktop.

### Domain-Specific Components
- **The "One Thing" Horizon Box**: An isolated container showcasing purely the single immediate task, dimming non-essential views.
- **Mindful Pause Bar**: A rhythmic breathing indicator integrated with a slow, looping gradient pulse between `#E8EFEA` and `#F3F0F8`.
- **Gentle Re-Entry Prompts**: Non-intrusive floating dialogs replacing timeout/session alerts: *"Take your time. We kept your place warm."*