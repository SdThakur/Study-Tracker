# Design System: Study Tracker

<!-- impeccable:design-schema 1 -->

## World

Focused Study & Notebook: A calm, exact, and distraction-free interface built for deliberate practice. Inspired by physical notebooks, reading rooms, and analog timers.

## Color Strategy

Restrained neutral ramp (warm graphite `#18181b` through warm off-white `#fbfbfb`) with subtle status accents.

- **Background Canvas**: `#fbfbfb`
- **Surface Cards**: `#ffffff` (bordered with hairline `#e4e4e7`)
- **Secondary Surfaces**: `#f4f4f5`
- **Primary Text**: `#18181b` (contrast ≥ 14:1)
- **Secondary Text**: `#52525b` (contrast ≥ 7:1)
- **Muted Text**: `#71717a` (contrast ≥ 4.5:1)
- **Streak Accent**: Amber `#d97706` (with `#fef3c7` tint)
- **Active / Success**: Emerald `#059669` (with `#d1fae5` tint)

## Typography

- **UI & Prose**: `Inter`, `-apple-system`, `sans-serif`
  - Body: 16px (1rem), line-height 1.5, regular (400)
  - Display / H1: 28px (1.75rem), line-height 2.125rem, semibold (600)
  - Section / H2: 20px (1.25rem), line-height 1.625rem, semibold (600)
  - Subhead / H3: 16px (1rem), line-height 1.375rem, medium (500)
- **Numerals, Clocks, & Metrics**: `JetBrains Mono`, `monospace` with `tabular-nums`
  - High-visibility focus timer: 60px–72px (3.75rem–4.5rem)
  - KPI Big Numbers: 24px (1.5rem), semibold (600)

## Layout & Spatial System

- **Scale**: Strict 4px base grid (4, 8, 12, 16, 20, 24, 32, 48, 64px)
- **Containers**:
  - Max page width: 1152px (`max-w-6xl`)
  - Container padding: 16px (`px-4`) mobile, 24px (`px-6`) desktop
- **Hierarchy of Surfaces**:
  - Main cards: 20px padding (`p-5`), outer radius 12px–16px (`rounded-xl`)
  - Inner items: 12px padding (`p-3`), inner radius 8px (`rounded-lg`)
  - Controls: 8px padding (`px-3 py-1.5`), radius 6px–8px (`rounded-md` / `rounded-lg`)

## Component Language

- **Quiet Chrome**: Navigation and borders stay quiet; color only appears in the weekly streak, timer state, and course progress bars.
- **Form Controls**: Crisp 1px hairlines (`#e4e4e7`), deepening to `#18181b` on focus without glowing halos.
- **Empty States**: Non-judgmental, clear calls to action prompting course creation or logging.
- **Motion**: Subtle feedback transitions (150ms ease) on background and opacity only; zero floating bounces or looping shimmers.
