// Sample AnalysisResponse used by the "Load sample result" button so the UI can
// be previewed without a running backend. Mirrors the real API shape.
export const mockImageUrl =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Chest_Xray_PA_3-8-2010.png/512px-Chest_Xray_PA_3-8-2010.png";

// Boxes are in original-pixel space of a ~2000x2000 chest film; the canvas
// rescales them to display size. (Coords are illustrative.)
export const mockResult = {
  final_analysis:
    `## Summary

The chest radiograph reveals several notable findings:

1. **Cardiomegaly** — The cardiac silhouette is significantly enlarged, consistent with the CV model's high-confidence detection (\`score = 0.81\`). This is well-supported by the patient's reported *shortness of breath*.
2. **Aortic enlargement** — Moderate confidence finding (\`score = 0.54\`) involving the mediastinal contour.
3. **Possible infiltrate** — A region of increased opacity in the right lower zone is compatible with the user's note, though this finding is of **moderate confidence** and warrants clinical correlation.

### Key Observations

- No pneumothorax or large pleural effusion is identified.
- The patient-reported shortness of breath is consistent with the cardiomegaly finding.

> **Note:** The infiltration finding (\`score = 0.32\`) has been downgraded from "definite" to "possible" after verification feedback.`,
  is_consistent: true,
  iterations: 2,
  verification_feedback: "CONSISTENT",
  cv_tool_raw_output: JSON.stringify({
    findings: [
      { label: "Cardiomegaly", score: 0.8123, box: [620, 980, 1380, 1560] },
      { label: "Aortic enlargement", score: 0.5412, box: [840, 560, 1180, 880] },
      { label: "Infiltration", score: 0.3187, box: [1180, 1180, 1620, 1560] },
    ],
  }),
  draft_analysis: "(superseded by final analysis)",
  messages: [
    "**Analytic draft (round 1):** The CV model reports:\n\n- **Cardiomegaly** — score `0.81`\n- **Aortic enlargement** — score `0.54`\n\nCombined with the user's report of *shortness of breath*, the enlarged cardiac silhouette is well supported. A low-confidence **Infiltration** (`0.32`) is noted but uncertain.",
    "**Verify (round 1):** The draft claims a \"definite infiltrate\" but the CV score is only `0.32` — this **overstates confidence**.\n\n> Please soften the infiltration claim and label it as *uncertain*.",
    "**Analytic draft (round 2):** Revised:\n\n1. Cardiomegaly stated as **well-supported**\n2. The right lower zone opacity is now described as a *possible infiltrate* of moderate-to-low confidence requiring clinical correlation.",
    "**Verify (round 2):** CONSISTENT",
  ],
};

