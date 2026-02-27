# ESKS-017 - Mobile Bottom Navigation fuer Kernrouten

- Status: `review`
- Prioritaet: `P2`
- Bereich: `frontend`
- Owner: `unassigned`

## Ziel / Business Value

Auf Mobilgeraeten sollen die wichtigsten Bereiche mit einem Daumen erreichbar sein. Das verbessert Navigationstempo und Session-Dauer.

## Kontext / Ist-Stand

- Aktuell existiert Mobile Header + Slide-In Drawer.
- Figma-Inspiration zeigt zusaetzlich eine fixe Bottom-Navigation fuer Kernrouten.
- Kernrouten sind derzeit `Dashboard`, `Lernen`, `Account`.

## Scope

- Bottom-Navigation nur auf mobilen Breakpoints.
- Aktiver Zustand pro Route klar hervorgehoben.
- Safe-Area-Unterstuetzung fuer iOS/Android Gestenbereiche.
- Zusammenspiel mit existierendem Drawer ohne doppelte Fokusfallen.

## Out of Scope

- Neudesign der Desktop-Navigation.
- Neue Routen ausserhalb der bestehenden Kernrouten.

## Technische Spezifikation

- Neue `MobileBottomNav` Komponente in `components/layout`.
- Mount innerhalb `AppShell` nur fuer authentifizierte Bereiche.
- Active State ueber `usePathname` (Prefix-Logik fuer Unterseiten).
- Main-Content bekommt ausreichendes Bottom-Padding, damit nichts verdeckt wird.

## API-Aenderungen

- `none`

## DB-/Migrations-Aenderungen

- `none`

## Frontend-Aenderungen

- `frontend/src/components/layout/app-shell.tsx`
- `frontend/src/components/layout/mobile-header.tsx`
- Neue `frontend/src/components/layout/mobile-bottom-nav.tsx`

## Infra-Aenderungen

- `none`

## Akzeptanzkriterien

- [x] Auf < md ist Bottom-Navigation sichtbar und klickbar.
- [x] Aktive Route ist visuell eindeutig.
- [x] Kein Content wird durch die Leiste abgeschnitten.
- [x] Drawer und Bottom-Navigation funktionieren konfliktfrei.

## Testplan

- Manuell auf iOS Safari + Chrome Android.
- Responsive Checks fuer typische Viewports (375x812, 390x844, 412x915).
- Accessibility Smoke: Tab-Reihenfolge, ARIA-Labels, Kontrast.

## Abhaengigkeiten

- Keine.

## Progress-Checklist

- [x] Component + Styles bauen.
- [x] In AppShell integrieren.
- [x] Layout-Padding/Safe-Area pruefen.
- [x] Mobile QA dokumentieren.

## Offene Fragen

- Soll der Drawer langfristig mobil entfallen oder als sekundares Menue bleiben?
