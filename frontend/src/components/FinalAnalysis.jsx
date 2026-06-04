import Markdown from "./Markdown.jsx";

export default function FinalAnalysis({ text }) {
  return (
    <div className="card final-card">
      <h3 className="card-title">Final Analysis</h3>
      {text ? (
        <Markdown className="final-text">{text}</Markdown>
      ) : (
        <p className="final-text">—</p>
      )}
    </div>
  );
}
