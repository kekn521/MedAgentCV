export default function ConsistencyBadge({ isConsistent, iterations }) {
  return (
    <div className={`badge ${isConsistent ? "badge-ok" : "badge-warn"}`}>
      <span className="badge-dot" />
      <span className="badge-text">
        {isConsistent ? "CONSISTENT" : "NOT CONSISTENT"}
      </span>
      <span className="badge-iter">{iterations} iter</span>
    </div>
  );
}
