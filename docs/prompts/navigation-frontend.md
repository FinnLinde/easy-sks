# Navigation Frontend — Session Prompt

## Context

Easy-SKS is a learning platform for the German SKS sailing license exam. The backend already has a complete **navigation domain** with API endpoints for practising the 10 official navigation exam sheets (Navigationsaufgaben). Each sheet has 16–18 connected tasks worth a total of 30 points, with a 90-minute time limit.

The navigation exam is 50% of the theoretical SKS exam. Unlike the existing flashcard-based Fragenkatalog (independent Q&A), navigation tasks form a **connected scenario**: a yacht trip where each task builds on the previous one. Users work on a **physical sea chart** (Übungskarte 49) with protractor and compass, then enter their calculated values (coordinates, courses, distances, etc.) into the app.

## What already exists

### Backend API (already built, tested, and wired)

7 endpoints under the `Navigation` tag (all require `freemium` role):

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/navigation-exams` | List the 10 sheet templates |
| `POST` | `/navigation-sessions` | Start a session `{ sheet_number, time_limit_minutes? }` |
| `GET` | `/navigation-sessions` | List completed session history for the user |
| `GET` | `/navigation-sessions/{session_id}` | Get session details with all tasks and answers |
| `PUT` | `/navigation-sessions/{session_id}/answers/{task_id}` | Save answer `{ student_answer }` |
| `POST` | `/navigation-sessions/{session_id}/submit` | Submit for evaluation, returns result |
| `GET` | `/navigation-sessions/{session_id}/result` | Get evaluated result |

**Important:** The navigation endpoints are implemented in the controller but **not yet declared in `openapi.yaml`**. You need to either add the navigation paths and schemas to the OpenAPI spec and regenerate types, or manually add the TypeScript types.

### Response shapes (exact fields from controller Pydantic models)

**NavigationTemplateOut** — `GET /navigation-exams` returns `list[NavigationTemplateOut]`:
```json
{
  "sheet_number": 1,
  "display_name": "Navigationsaufgabe 1",
  "task_count": 18,
  "total_points": 30,
  "time_limit_minutes": 90
}
```

**NavigationSessionOut** — `POST /navigation-sessions` and `GET /navigation-sessions/{session_id}`:
```json
{
  "session_id": "uuid",
  "sheet_number": 1,
  "status": "in_progress",
  "started_at": "ISO datetime",
  "submitted_at": "ISO datetime | null",
  "deadline_at": "ISO datetime",
  "time_limit_minutes": 90,
  "time_remaining_seconds": 5400,
  "time_over": false,
  "task_count": 18,
  "questions": [NavigationQuestionOut]
}
```

**NavigationQuestionOut** — each question within a session:
```json
{
  "task_number": 1,
  "task_id": "string",
  "points": 2,
  "context": "Die Yacht 'Albatros' liegt am 15. Juni um 08:00 Uhr...",
  "sub_questions": [{ "text": "Bestimmen Sie den Kartenkurs (KaK).", "points": 1 }],
  "student_answer": "",
  "answered_at": "ISO datetime | null"
}
```

**SaveNavigationAnswerOut** — `PUT /navigation-sessions/{session_id}/answers/{task_id}`:
```json
{
  "session_id": "uuid",
  "task_id": "string",
  "task_number": 1,
  "student_answer": "KaK = 245°",
  "answered_at": "ISO datetime | null"
}
```

**NavigationResultOut** — `POST .../submit` and `GET .../result`:
```json
{
  "session_id": "uuid",
  "sheet_number": 1,
  "status": "evaluated",
  "started_at": "ISO datetime",
  "submitted_at": "ISO datetime | null",
  "time_limit_minutes": 90,
  "time_over": false,
  "total_score": 24.0,
  "max_score": 30.0,
  "passed": true,
  "pass_score_threshold": 21.0,
  "questions": [NavigationQuestionResultOut]
}
```

**NavigationQuestionResultOut** — each question within a result:
```json
{
  "task_number": 1,
  "task_id": "string",
  "context": "Die Yacht 'Albatros'...",
  "sub_questions": ["Bestimmen Sie den Kartenkurs (KaK)."],
  "key_answers": ["KaK = 245° (± 1°)"],
  "solution_text": "Full reference solution text from the official PDF...",
  "student_answer": "KaK = 245°",
  "score": 2.0,
  "max_score": 2.0,
  "is_correct": true,
  "feedback": "Richtig"
}
```

Note: in the result view, `sub_questions` is `list[string]` (just the text), not `list[{text, points}]` like in the session view.

**Important**: `solution_text` is always populated — it contains the full official Musterlösung from the PDF. `key_answers` only contains the numeric tolerance values (e.g. `KaK = 286° [± 1°]`) and may be empty for descriptive tasks. Always show `solution_text` as the reference solution in the result view.

**NavigationSessionHistoryOut** — `GET /navigation-sessions` returns `list[NavigationSessionHistoryOut]`:
```json
{
  "session_id": "uuid",
  "sheet_number": 1,
  "status": "evaluated",
  "started_at": "ISO datetime",
  "submitted_at": "ISO datetime | null",
  "total_score": 24.0,
  "max_score": 30.0,
  "passed": true,
  "time_over": false
}
```

### Frontend (existing patterns to follow)

- **Framework**: Next.js 16 (App Router), React 19, Tailwind CSS v4, Radix UI, shadcn
- **Dark theme** by default, semantic color variables
- **Existing exam simulator** at `components/exams/exam-simulator.tsx` — this is the pattern to follow. It has three views: setup → active → result, driven by a `view` state.
- **API client**: `services/api/client.ts` uses `openapi-fetch` with typed paths from `schema.ts`
- **Service pattern**: each domain has `services/<domain>/<domain>-service.ts` that wraps API calls
- **Page pattern**: `app/<route>/page.tsx` wraps a feature component with `AuthGuard`
- **Layout**: `AppShell` with `Sidenav` + `MobileBottomNav`, nav items in `nav-config.tsx`

### Key structural differences from the exam simulator

| Aspect | Exam (Fragenkatalog) | Navigation |
|--------|---------------------|------------|
| Questions | 30 independent Q&A flashcards | 16–18 connected tasks forming a scenario |
| Points | Uniform 2 pts per question (60 total) | Variable 1–3 pts per task (30 total) |
| Pass threshold | 39/60 | 21/30 (70%) |
| Question content | Single `question_text` string | `context` + list of `sub_questions` with individual points |
| Answer format | Free-text paragraph | Short calculated values (coordinates, courses, distances) |
| ID field | `card_id` | `task_id` |
| Result extras | `errors[]` list | `key_answers[]` (official solutions with tolerances) |
| Physical materials | None | Requires Übungskarte 49, protractor, compass |

## Task

Build the frontend for the navigation domain. This involves:

### 1. Navigation service (`services/navigation/navigation-service.ts`)

Create an API service following the existing `exam-service.ts` pattern. Each function uses `apiClient` from `@/services/api/client`, returns the unwrapped data, and throws on error.

Functions needed:

```typescript
import { apiClient } from "@/services/api/client";

// Type aliases — either import from schema.ts or define manually
export type NavigationTemplate = { sheet_number: number; display_name: string; task_count: number; total_points: number; time_limit_minutes: number };
export type NavigationSession = { session_id: string; sheet_number: number; status: string; started_at: string; submitted_at: string | null; deadline_at: string; time_limit_minutes: number; time_remaining_seconds: number; time_over: boolean; task_count: number; questions: NavigationQuestion[] };
export type NavigationQuestion = { task_number: number; task_id: string; points: number; context: string; sub_questions: { text: string; points: number }[]; student_answer: string; answered_at: string | null };
export type NavigationResult = { session_id: string; sheet_number: number; status: string; started_at: string; submitted_at: string | null; time_limit_minutes: number; time_over: boolean; total_score: number; max_score: number; passed: boolean; pass_score_threshold: number; questions: NavigationQuestionResult[] };
export type NavigationQuestionResult = { task_number: number; task_id: string; context: string; sub_questions: string[]; key_answers: string[]; student_answer: string; score: number; max_score: number; is_correct: boolean; feedback: string };
export type NavigationSessionHistory = { session_id: string; sheet_number: number; status: string; started_at: string; submitted_at: string | null; total_score: number | null; max_score: number | null; passed: boolean | null; time_over: boolean };
```

Service functions (follow the same `{ data, error }` destructuring as `exam-service.ts`):

- `listNavigationTemplates()` → `GET /navigation-exams` → returns `NavigationTemplate[]`
- `startNavigationSession(sheetNumber, timeLimitMinutes?)` → `POST /navigation-sessions` → returns `NavigationSession`
- `getNavigationSession(sessionId)` → `GET /navigation-sessions/{session_id}` → returns `NavigationSession`
- `saveNavigationAnswer(sessionId, taskId, studentAnswer)` → `PUT /navigation-sessions/{session_id}/answers/{task_id}` → returns `void`
- `submitNavigationSession(sessionId)` → `POST /navigation-sessions/{session_id}/submit` → returns `NavigationResult`
- `getNavigationResult(sessionId)` → `GET /navigation-sessions/{session_id}/result` → returns `NavigationResult`
- `listNavigationHistory()` → `GET /navigation-sessions` → returns `NavigationSessionHistory[]`

Since the navigation endpoints are **not yet in `openapi.yaml`**, use typed manual fetch calls with the apiClient. The path strings must match exactly. Once the OpenAPI spec is updated, these can be migrated to use schema-derived types.

### 2. OpenAPI schema update

The navigation endpoints are implemented in `backend/navigation/controller/navigation_controller.py` but **not declared in `backend/openapi.yaml`** yet. Two options:

**Option A (preferred):** Add the navigation paths and schemas to `openapi.yaml`, then regenerate:
```bash
npx openapi-typescript ../backend/openapi.yaml -o src/services/api/schema.ts
```

**Option B:** Define the TypeScript types manually in the navigation service file (as shown above) and use untyped fetch calls via the apiClient. This avoids touching the OpenAPI spec but loses type safety on the API paths.

### 3. Navigation simulator component (`components/navigation/navigation-simulator.tsx`)

Follow the **same three-view pattern** as `exam-simulator.tsx`: a `"use client"` component with a `view` state cycling through `"setup" | "active" | "result"`.

#### State structure

Mirror the exam simulator's state approach but adapt the identifiers:

```typescript
type NavigationView = "setup" | "active" | "result";

// Setup
const [view, setView] = useState<NavigationView>("setup");
const [templates, setTemplates] = useState<NavigationTemplate[]>([]);
const [history, setHistory] = useState<NavigationSessionHistory[]>([]);
const [selectedSheet, setSelectedSheet] = useState<number | null>(null);

// Active session
const [activeSession, setActiveSession] = useState<NavigationSession | null>(null);
const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
const [answersByTask, setAnswersByTask] = useState<Record<string, string>>({});
const [dirtyTaskIds, setDirtyTaskIds] = useState<Set<string>>(new Set());

// Result
const [result, setResult] = useState<NavigationResult | null>(null);
```

Key difference from exam simulator: use `task_id` instead of `card_id` as the answer map key.

#### Setup view

- Show the 10 available navigation sheets as selectable cards or a dropdown (match exam-simulator style)
- Each entry: "Navigationsaufgabe 1–10", task count, 30 points, 90 min
- Info panel showing the selected sheet details (time limit, task count, pass threshold of 21/30)
- **Material notice** — prominently display an info box:
  > "Halte Übungskarte 49 (INT 1463), Kursdreieck, Anlegedreieck und Zirkel bereit."
- Show a "Simulation starten" button
- History section with completed sessions: sheet number, score, pass/fail badge, date, and a "Ergebnis ansehen" button
- An incomplete sheet (task_count doesn't match expected) should be flagged and not startable

#### Active view

Two-column layout matching the exam simulator (`lg:grid-cols-[280px_1fr]`):

**Left sidebar:**
- Sheet identifier: "Navigationsaufgabe {sheet_number}"
- Countdown timer (compute from `deadline_at`, use `setInterval` tick pattern from exam simulator)
- Time-over warning in red when expired
- Task grid: numbered buttons (1–N) showing answered/current/unanswered state
  - Current task: sky-blue highlight (`border-sky-400 bg-sky-500/20`)
  - Answered: green (`border-emerald-500/40 bg-emerald-500/15`)
  - Unanswered: neutral
  - Show the **point value** inside or below each button since tasks have variable points

**Right content area:**
- Header: "Aufgabe {task_number} von {task_count}" with the point value badge (e.g., "[2 Pt.]")
- **Context block** — the scenario/narrative text in a styled box. This is crucial: navigation tasks describe a yacht trip and users need this context to work on the chart. Use a distinct background to make it stand out.
- **Sub-questions list** — below the context, list each sub-question with its individual point value:
  ```
  • [1 Pt.] Bestimmen Sie den Kartenkurs (KaK).
  • [1 Pt.] Bestimmen Sie die Distanz.
  ```
- **Answer textarea** — shorter than the exam textarea since answers are compact values. `min-h-24` instead of `min-h-44`. Placeholder: "Trage hier deine Antwort ein..."
- Save status indicator (same pattern: "Gespeichert" / "Nicht gespeichert" / "Speichere...")
- Navigation buttons: Zurück / Weiter / Prüfung abgeben

**Auto-save:** Use the same dirty-tracking pattern as the exam simulator. On question navigation, flush the current dirty answer via `saveNavigationAnswer()`. Before submit, flush all remaining dirty answers.

#### Result view

- **Summary card** with 4 KPI tiles (reuse the `ResultKpi` helper pattern):
  - Punktzahl: `{total_score} / {max_score}`
  - Bestehen: `{pass_score_threshold} Punkte`
  - Status: Bestanden / Nicht bestanden (green/red)
  - Zeitlimit: Eingehalten / Überschritten (green/red)
- Time-over banner if applicable
- **Per-task breakdown** — for each question, a card showing:
  - Task header: "Aufgabe {task_number}" with score badge (`{score} / {max_score}`)
  - Context text (shorter/collapsed since users already read it)
  - Sub-questions listed
  - **Student answer** labeled "Deine Antwort"
  - **Musterlösung** (`solution_text`) — the full official reference solution, always displayed in a **distinct styled block** (e.g., emerald/green-tinted border and background). This is the most valuable learning element — it shows the complete calculation steps and reasoning. Always present for every task, including descriptive ones.
  - If `key_answers` are present (numeric values with tolerances), highlight them visually within or alongside the solution, e.g.:
    ```
    Schlüsselwerte:
    • KaK = 245° [± 1°]
    • Distanz = 12,4 sm [± 0,2 sm]
    ```
  - AI feedback text with correct/incorrect icon (CheckCircle2 / XCircle)
- "Zurück zur Auswahl" button to return to setup (reset state, reload templates + history)

### 4. Navigation page (`app/navigation/page.tsx`)

Create a thin page route at `/navigation` following the exact `exams/page.tsx` pattern:

```typescript
import { AuthGuard } from "@/components/auth/auth-guard";
import { NavigationSimulator } from "@/components/navigation/navigation-simulator";

export default function NavigationPage() {
  return (
    <div className="min-h-full w-full">
      <AuthGuard description="Melde dich an, um eine Navigationsprüfung zu starten.">
        <NavigationSimulator />
      </AuthGuard>
    </div>
  );
}
```

### 5. Add navigation to the nav config

Add a "Navigation" item to `components/layout/nav-config.tsx` between "Prüfung" and "Account". Use the `Compass` icon from lucide-react:

```typescript
import { BookOpen, ClipboardCheck, Compass, LayoutDashboard, User } from "lucide-react";

export const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard, requiredRole: "freemium" },
  { href: "/study", label: "Lernen", icon: BookOpen, requiredRole: "freemium" },
  { href: "/exams", label: "Prüfung", icon: ClipboardCheck, requiredRole: "freemium" },
  { href: "/navigation", label: "Navigation", icon: Compass, requiredRole: "freemium" },
  { href: "/account", label: "Account", icon: User, requiredRole: "freemium" },
] as const satisfies readonly { href: string; label: string; icon: LucideIcon; requiredRole?: AuthRole }[];
```

## Design guidance

- **Consistency**: match the exam simulator's card styles, colors, spacing, and dark-theme treatment exactly (`border-white/10 bg-card/70`, `bg-background/40`, etc.)
- **Context prominence**: the narrative context block is the core of each task — use a slightly larger/padded card to make it feel like reading a scenario, not just a question
- **Sub-questions**: render as a styled list with individual point badges so users can see what each sub-answer is worth
- **Compact answers**: use a shorter textarea (`min-h-24`) since navigation answers are typically single-line values, not paragraphs
- **Variable points**: show point values on the task grid buttons and in the task header — this differs from the theory exam where all questions are uniformly 2 points
- **Key answers in results**: these are the single most valuable learning element. Display in a clearly distinct block (e.g., `border-emerald-500/30 bg-emerald-500/10 p-3`) so they stand out from the student's answer
- **Material reminder**: the setup view must remind users to prepare physical materials. This is a hard requirement — without the chart, the tasks are meaningless
- **German UI text**: all labels and messages in German, matching existing conventions (Bestanden, Nicht bestanden, Prüfung abgeben, etc.)
- **Page header**: use "Navigationsaufgaben" as the h1, with subtitle "16–18 Aufgaben pro Bogen, 30 Punkte. Bestanden ab 21 Punkten."

## Files to create/modify

**Create:**
- `src/services/navigation/navigation-service.ts`
- `src/components/navigation/navigation-simulator.tsx`
- `src/app/navigation/page.tsx`

**Modify:**
- `src/services/api/schema.ts` (regenerate or add navigation types)
- `src/components/layout/nav-config.tsx` (add Navigation nav item)

## Reference: exam-service.ts (pattern to follow)

The existing exam service at `src/services/exam/exam-service.ts` uses this exact pattern — replicate it for navigation:

```typescript
import { apiClient } from "@/services/api/client";

export async function listExamTemplates(): Promise<ExamTemplate[]> {
  const { data, error } = await apiClient.GET("/exams");
  if (error || !data) throw new Error("Failed to fetch exam templates");
  return data;
}

export async function startExamSession(sheetNumber: number, timeLimitMinutes?: number): Promise<ExamSession> {
  const { data, error } = await apiClient.POST("/exam-sessions", {
    body: { sheet_number: sheetNumber, ...(timeLimitMinutes ? { time_limit_minutes: timeLimitMinutes } : {}) },
  });
  if (error || !data) throw new Error("Failed to start exam session");
  return data;
}

// ... same pattern for all other functions
```

## Reference: exam-simulator.tsx (pattern to follow)

The existing exam simulator at `src/components/exams/exam-simulator.tsx` (588 lines) uses these patterns that the navigation simulator should replicate:

- **View state**: `type ExamView = "setup" | "active" | "result"` with a single `view` state driving conditional rendering
- **Setup loading**: `loadSetup()` callback that fetches templates + history in parallel via `Promise.all`
- **Timer**: `useEffect` with `setInterval` on 1-second tick, computing remaining seconds from `deadline_at`
- **Dirty tracking**: `answersByCard` (Record<string, string>) + `dirtyCardIds` (Set<string>) for auto-save
- **Flush on navigate**: `flushCard(cardId)` called before changing `currentQuestionIndex`
- **Flush all before submit**: `flushAllDirtyAnswers()` called before `submitExamSession()`
- **History result view**: `handleOpenHistoryResult(sessionId)` fetches and displays a past result
- **Back to selection**: `handleBackToSelection()` resets all state and reloads setup data
- **ResultKpi helper**: small component for the 4 KPI tiles in the result view
- **formatDuration helper**: converts seconds to "MM:SS" string
