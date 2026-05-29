const COLORS = ["#36e0c8", "#ffb454", "#ff6b8b", "#7aa2ff", "#c792ea"];

export default function FindingsList({ findings }) {
  return (
    <div className="card">
      <h3 className="card-title">CV Findings</h3>
      {findings.length === 0 ? (
        <p className="muted">No finding.</p>
      ) : (
        <ul className="findings">
          {findings.map((f, i) => (
            <li key={i} className="finding">
              <span
                className="finding-swatch"
                style={{ background: COLORS[i % COLORS.length] }}
              />
              <span className="finding-label">{f.label}</span>
              <span className="finding-score">{(f.score * 100).toFixed(1)}%</span>
              <span className="finding-box">
                [{f.box.map((c) => Math.round(c)).join(", ")}]
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
