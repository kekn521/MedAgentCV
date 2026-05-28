import { useState } from "react";
import Header from "./components/Header.jsx";
import InputPanel from "./components/InputPanel.jsx";
import ImageWithBoxes from "./components/ImageWithBoxes.jsx";
import ConsistencyBadge from "./components/ConsistencyBadge.jsx";
import FinalAnalysis from "./components/FinalAnalysis.jsx";
import FindingsList from "./components/FindingsList.jsx";
import AgentTimeline from "./components/AgentTimeline.jsx";
import RawJson from "./components/RawJson.jsx";
// FollowUpBar (multi-turn) is hidden until the backend supports sessions.
// import FollowUpBar from "./components/FollowUpBar.jsx";
import { mockResult, mockImageUrl } from "./mockResult.js";

// status: "idle" | "loading" | "success" | "error"
export default function App() {
  const [status, setStatus] = useState("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const [imageUrl, setImageUrl] = useState(null);
  const [result, setResult] = useState(null);

  function parseFindings(raw) {
    if (!raw) return [];
    try {
      const obj = JSON.parse(raw);
      return Array.isArray(obj.findings) ? obj.findings : [];
    } catch {
      return [];
    }
  }

  async function handleAnalyze({ file, description }) {
    setStatus("loading");
    setErrorMsg("");
    setResult(null);
    setImageUrl(URL.createObjectURL(file));

    const body = new FormData();
    body.append("image", file);
    body.append("disease_description", description);

    try {
      const res = await fetch("/api/v1/analyze", { method: "POST", body });
      if (!res.ok) {
        throw new Error(`Server responded ${res.status} ${res.statusText}`);
      }
      const data = await res.json();
      setResult(data);
      setStatus("success");
    } catch (err) {
      setErrorMsg(err.message || "Request failed");
      setStatus("error");
    }
  }

  function loadSample() {
    setImageUrl(mockImageUrl);
    setResult(mockResult);
    setErrorMsg("");
    setStatus("success");
  }

  const findings = result ? parseFindings(result.cv_tool_raw_output) : [];

  return (
    <div className="app">
      <div className="grain" aria-hidden="true" />
      <Header onLoadSample={loadSample} />

      <main className="workspace">
        <section className="panel input-col">
          <InputPanel onAnalyze={handleAnalyze} loading={status === "loading"} />
          {imageUrl && (
            <ImageWithBoxes imageUrl={imageUrl} findings={findings} />
          )}
        </section>

        <section className="panel output-col">
          <div className="output-head">
            <h2 className="col-title">Diagnostic Output</h2>
            {status === "success" && result && (
              <ConsistencyBadge
                isConsistent={result.is_consistent}
                iterations={result.iterations}
              />
            )}
          </div>

          {status === "idle" && (
            <div className="placeholder">
              <p>Upload a chest X-ray and a description, then run the agent.</p>
              <p className="muted">
                No backend running? Hit <strong>Load sample result</strong> in the
                header to preview the interface.
              </p>
            </div>
          )}

          {status === "loading" && (
            <div className="placeholder">
              <div className="scanner" />
              <p>Agent is analyzing the radiograph…</p>
              <p className="muted">This can take several seconds.</p>
            </div>
          )}

          {status === "error" && (
            <div className="error-box">
              <strong>Analysis failed.</strong>
              <p>{errorMsg}</p>
              <p className="muted">
                Is the backend running at <code>127.0.0.1:8000</code>? You can
                still preview the UI via <strong>Load sample result</strong>.
              </p>
            </div>
          )}

          {status === "success" && result && (
            <div className="output-stack">
              <FinalAnalysis text={result.final_analysis} />
              <FindingsList findings={findings} />
              <AgentTimeline messages={result.messages || []} />
              <RawJson raw={result.cv_tool_raw_output} />
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
