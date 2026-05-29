export default function FinalAnalysis({ text }) {
  return (
    <div className="card final-card">
      <h3 className="card-title">Final Analysis</h3>
      <p className="final-text">{text || "—"}</p>
    </div>
  );
}
