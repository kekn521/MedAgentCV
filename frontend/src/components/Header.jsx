import {
  projectTitle,
  projectSubtitle,
  teamNumber,
  teamMembers,
} from "../teamConfig.js";

export default function Header({ onLoadSample }) {
  return (
    <header className="header">
      <div className="header-main">
        <div className="brand">
          <span className="brand-mark">◢◤</span>
          <div>
            <h1 className="title">{projectTitle}</h1>
            <p className="subtitle">{projectSubtitle}</p>
          </div>
        </div>
        <div className="header-actions">
          <span className="team-chip">TEAM {teamNumber}</span>
          <button className="ghost-btn" onClick={onLoadSample}>
            Load sample result
          </button>
        </div>
      </div>

      <ul className="members">
        {teamMembers.map((m) => (
          <li key={m.id} className="member">
            <span className="member-name">{m.name}</span>
            <span className="member-id">{m.id}</span>
          </li>
        ))}
      </ul>
    </header>
  );
}
