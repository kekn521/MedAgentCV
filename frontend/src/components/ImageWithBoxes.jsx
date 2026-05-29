import { useEffect, useRef, useState } from "react";

// Palette cycled per finding so each box/label is distinguishable.
const COLORS = ["#36e0c8", "#ffb454", "#ff6b8b", "#7aa2ff", "#c792ea"];

export default function ImageWithBoxes({ imageUrl, findings }) {
  const canvasRef = useRef(null);
  const [dims, setDims] = useState({ w: 0, h: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      // Fit within a max display width while keeping aspect ratio.
      const maxW = 520;
      const scale = Math.min(1, maxW / img.naturalWidth);
      const dispW = Math.round(img.naturalWidth * scale);
      const dispH = Math.round(img.naturalHeight * scale);
      canvas.width = dispW;
      canvas.height = dispH;
      setDims({ w: dispW, h: dispH });

      ctx.clearRect(0, 0, dispW, dispH);
      ctx.drawImage(img, 0, 0, dispW, dispH);

      findings.forEach((f, i) => {
        if (!Array.isArray(f.box) || f.box.length !== 4) return;
        const [x1, y1, x2, y2] = f.box.map((c) => c * scale);
        const color = COLORS[i % COLORS.length];

        ctx.lineWidth = 2;
        ctx.strokeStyle = color;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        const label = `${f.label} ${(f.score * 100).toFixed(0)}%`;
        ctx.font = "600 12px 'JetBrains Mono', monospace";
        const padX = 5;
        const tw = ctx.measureText(label).width + padX * 2;
        const ty = y1 - 18 < 0 ? y1 + 2 : y1 - 18;
        ctx.fillStyle = color;
        ctx.fillRect(x1, ty, tw, 16);
        ctx.fillStyle = "#06120f";
        ctx.fillText(label, x1 + padX, ty + 12);
      });
    };
    img.onerror = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };
    img.src = imageUrl;
  }, [imageUrl, findings]);

  return (
    <div className="viewer">
      <div className="viewer-head">
        <span>Image · detection overlay</span>
        <span className="muted">{findings.length} finding(s)</span>
      </div>
      <div className="viewer-frame" style={{ width: dims.w || "auto" }}>
        <canvas ref={canvasRef} className="viewer-canvas" />
        <div className="crosshair" aria-hidden="true" />
      </div>
    </div>
  );
}
