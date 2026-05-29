// messages is a flat alternating list: even index = analytic draft,
// odd index = verify feedback. Pair them into rounds for display.
function toRounds(messages) {
  const rounds = [];
  for (let i = 0; i < messages.length; i += 2) {
    rounds.push({
      round: i / 2 + 1,
      analytic: messages[i],
      verify: messages[i + 1],
    });
  }
  return rounds;
}

export default function AgentTimeline({ messages }) {
  const rounds = toRounds(messages);
  return (
    <div className="card">
      <h3 className="card-title">Agent Dialogue · analytic ↔ verify</h3>
      {rounds.length === 0 ? (
        <p className="muted">No agent messages.</p>
      ) : (
        <ol className="timeline">
          {rounds.map((r) => (
            <li key={r.round} className="round">
              <div className="round-tag">Round {r.round}</div>
              {r.analytic && (
                <div className="turn turn-analytic">
                  <span className="turn-role">ANALYTIC</span>
                  <p>{r.analytic}</p>
                </div>
              )}
              {r.verify && (
                <div
                  className={`turn turn-verify ${
                    r.verify.trim().toUpperCase().startsWith("CONSISTENT")
                      ? "verify-ok"
                      : "verify-flag"
                  }`}
                >
                  <span className="turn-role">VERIFY</span>
                  <p>{r.verify}</p>
                </div>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
