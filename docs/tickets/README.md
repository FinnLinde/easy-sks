# EasySKS Ticket Backlog

Diese Tickets dienen als Spezifikation und Arbeitsgrundlage fuer die technische Umsetzung mit einem Coding-Agent.

## Statuswerte

- `todo`: noch nicht begonnen
- `in_progress`: aktive Umsetzung
- `blocked`: extern blockiert (z. B. fehlende Inhalte/Entscheidungen)
- `review`: umgesetzt, wartet auf Review/QA
- `done`: abgeschlossen

## Priorisierte Reihenfolge (Start)

1. `ESKS-012` New Card Limit / Einfuehrungs-Queue (Learning-MVP priorisiert)
2. `ESKS-013` Practice Mode / Lernen jederzeit
3. `ESKS-014` Due-Queue Ordering / deterministische Reihenfolge
4. `ESKS-015` Review-Log Persistenz / Observability
5. `ESKS-001` Multi-User-Fortschritt einführen (kritische Grundlage)
6. `ESKS-002` Frontend Login + Token-Injektion
7. `ESKS-003` User-Provisioning & Entitlement-Basis
8. `ESKS-004` Freemium-Regeln & Enforcement
9. `ESKS-005` Abo-Zahlung (Stripe) + Premium-Freischaltung
10. `ESKS-006` Dashboard MVP
11. `ESKS-007` Strukturierte Lernpfade/Kategorien
12. `ESKS-008` Pruefungssimulation MVP
13. `ESKS-009` KI-Antwortbewertung (Text) MVP
14. `ESKS-010` Spracheingabe + Transkription
15. `ESKS-011` Produktions-Infrastruktur-Basis
16. `ESKS-016` Study Session UX States (Setup/Completion/Welcome)
17. `ESKS-017` Mobile Bottom Navigation
18. `ESKS-018` Dashboard Insights API
19. `ESKS-019` Account Plan Status und Billing Surface

## Hinweise fuer Agenten

- Progress immer im Ticket selbst unter `Progress-Checklist` und `Status` aktualisieren.
- Scope nicht stillschweigend erweitern; neue Anforderungen als Folge-Ticket erfassen.
- Bei DB- oder API-Aenderungen immer Migrationen, Tests und Dokumentation mitziehen.
- Vor groesseren Architekturentscheidungen `Offene Fragen` und `Abhaengigkeiten` pruefen.
