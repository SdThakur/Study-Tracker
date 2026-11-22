# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Lightweight Modern Web App (HTML5, Tailwind CSS, Vanilla JS) embedded directly in FastAPI via StaticFiles and Jinja2 / HTML response. Runs seamlessly in Docker without Node build steps.

## Users

Students, self-directed learners, and software engineers tracking curriculum progress, managing courses, logging study sessions, and maintaining weekly study streaks.

## Product Purpose

Provide an authenticated, focused, and distraction-free study companion to record course progress, log study sessions, and visualize study habits and streaks.

## Positioning

An intentional, clean study companion built around user ownership and calm focus—eschewing bloated SaaS mechanics in favor of fast logging, streak accountability, and clear progress analytics.

## Operating Context

Desktop and mobile browsers during or immediately following study blocks. Demands fast authentication, sub-second logging, responsive layout, and clear feedback.

## Capabilities and Constraints

- Authenticated session management with JWT tokens stored securely in client storage.
- Course management (add, edit, delete, list) with user isolation.
- Study session logging (course, minutes, date, notes) with filtering.
- Interactive Study Timer (start, pause, complete session directly into the database).
- Live analytics: total hours/minutes, course distribution, and consecutive weekly study streak.
- Compatible with existing FastAPI backend and Docker container without additional build tooling.

## Brand Commitments

- Name: Study Tracker
- Tone: Calm, exact, focused, warm library/notebook feel.
- Palette: Warm graphite neutrals, parchment/warm card surfaces, deep ink accent. Zero emojis, zero vibrating gradient text, zero glowing borders.

## Product Principles

- Rapid Logging: Logging a session should take seconds, never interrupting flow.
- Calm Interface: Quiet chrome so study metrics and focus take center stage.
- Honest Accountability: Clear metrics on actual time spent and streak continuity.
