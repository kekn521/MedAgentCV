// Multi-turn follow-up is reserved for when the backend gains session support.
// Disabled for now per the design spec.
export default function FollowUpBar() {
  return (
    <footer className="followup">
      <input
        className="followup-input"
        placeholder="Ask a follow-up question…"
        disabled
      />
      <button className="followup-btn" disabled>
        Send
      </button>
      <span className="followup-note">Multi-turn pending backend support</span>
    </footer>
  );
}
