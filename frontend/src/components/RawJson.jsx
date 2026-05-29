import { useState } from "react";

export default function RawJson({ raw }) {
  const [open, setOpen] = useState(false);

  let pretty = raw;
  try {
    pretty = JSON.stringify(JSON.parse(raw), null, 2);
  } catch {
    /* keep as-is */
  }

  return (
    <div className="card">
      <button className="collapse-btn" onClick={() => setOpen((o) => !o)}>
        <span>{open ? "▾" : "▸"}</span> Raw CV tool output
      </button>
      {open && <pre className="raw-json">{pretty || "—"}</pre>}
    </div>
  );
}
