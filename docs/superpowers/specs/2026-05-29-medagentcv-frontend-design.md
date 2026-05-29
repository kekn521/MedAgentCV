# MedAgentCV Frontend — Design Spec

**Date:** 2026-05-29
**Scope:** Frontend only. Backend is owned by other team members and is not modified.

## Purpose

Build a simple React + Vite single-page app that lets a user run the existing
chest X-ray diagnosis agent and clearly illustrates the **input** and the
agent's **output** (including the internal analytic↔verify dialogue) for a live
demo. "Keep it simple" is an explicit constraint — no over-engineering.

## Backend Contract (existing, unchanged)

- **Endpoint:** `POST /api/v1/analyze` (multipart/form-data), served by FastAPI
  at `http://127.0.0.1:8000`.
- **Request fields:**
  - `image`: image file (PNG/JPG; backend also supports DICOM).
  - `disease_description`: text (3–500 chars).
- **Response (`AnalysisResponse`):**
  - `final_analysis: string`
  - `is_consistent: boolean`
  - `iterations: number`
  - `verification_feedback: string | null`
  - `cv_tool_raw_output: string | null` — JSON string:
    `{"findings": [{"label": str, "score": float, "box": [x1,y1,x2,y2]}, ...]}`,
    box coords in **original image pixel space**, sorted by score desc.
  - `draft_analysis: string | null`
  - `messages: string[]` — flat list, alternating: even index = analytic draft,
    odd index = verify feedback. Length grows with each loop iteration.

The agent is **single-shot**: one image + description → one response. There is
no session/conversation-history concept yet.

## Decisions

- **CORS:** Use Vite dev-server proxy (`/api` → `http://127.0.0.1:8000`). No
  backend changes. (Approach A.)
- **Stack:** React + Vite, **JSX (not TypeScript)**, **plain CSS** (no Tailwind,
  no component library).
- **Location:** existing `frontend/` directory.
- **Findings display:** overlay bounding boxes on the uploaded image **plus** a
  findings list.
- **Multi-turn:** out of scope for now (backend not ready). Reserve a disabled
  follow-up input in the UI, labeled as pending backend support.

## Layout (single page)

```
┌──────────────────────────────────────────────────────────┐
│  Header: "title"  ·  Team 12                              │
│  Members: Kai-Yuan Lin (111000169), Shang-Che Hsieh      │
│  (X1146020), Hai-Yun Chang (111000209), Shi-Jie Ng       │
│  (111000263), Jen-Chun Cheng (108062124)                 │
├───────────────────────┬──────────────────────────────────┤
│  INPUT                 │  OUTPUT                           │
│  · image upload        │  · consistency badge + iterations │
│  · description textarea│  · Final Analysis panel           │
│  · Analyze button      │  · Findings list                  │
│  · image preview with  │  · Agent dialogue timeline        │
│    detection boxes     │    (analytic ↔ verify rounds)     │
│                        │  · raw CV JSON (collapsible)       │
├───────────────────────┴──────────────────────────────────┤
│  Follow-up input (disabled — "multi-turn pending backend") │
└──────────────────────────────────────────────────────────┘
```

## Components

- `App` — top-level state machine (`idle | loading | success | error`), holds
  the response and the selected image.
- `Header` — project title (`"title"` placeholder), team number, members +
  student IDs.
- `InputPanel` — file input, description textarea, Analyze button; validates
  description length (3–500) and that an image is selected.
- `ImageWithBoxes` — `<canvas>` that draws the uploaded image and overlays
  detection rectangles (label + score). Handles scaling from original pixel
  space to displayed canvas size.
- `ConsistencyBadge` — green "Consistent" / amber "Not consistent", shows
  `iterations`.
- `FinalAnalysis` — renders `final_analysis` prominently.
- `FindingsList` — table/list of `{label, score, box}` from parsed
  `cv_tool_raw_output`.
- `AgentTimeline` — pairs `messages` into rounds (analytic draft + verify
  feedback) so the review loop is visible.
- `RawJson` — collapsible view of `cv_tool_raw_output`.
- `FollowUpBar` — disabled text input with a "pending backend" note.

## Data Flow

1. User selects an image and types a description.
2. Click Analyze → build `FormData` → `POST /api/v1/analyze` → state `loading`
   (spinner; analysis can take seconds to tens of seconds).
3. On success: parse JSON, parse `cv_tool_raw_output` into findings, render all
   output panels; draw boxes on canvas.
4. On error (network / non-2xx): state `error`, show a readable message; keep
   the input so the user can retry.

## Error Handling

- Missing image or description, or description outside 3–500 chars → inline
  validation, block submit.
- Fetch failure / non-2xx → error banner with status text.
- `cv_tool_raw_output` null or unparseable → show "No CV findings available"
  and skip box drawing.
- Empty `findings` → "No finding" message, no boxes.

## Testing

- Manual demo run against the live backend (primary acceptance).
- Component-level sanity: render with a mocked `AnalysisResponse` fixture
  (including a multi-iteration `messages` array and several findings) to verify
  box overlay, timeline pairing, and badge states without needing the backend.

## Out of Scope

- Any backend modification.
- Real multi-turn conversation / session history.
- Authentication, persistence, deployment config beyond local dev.
