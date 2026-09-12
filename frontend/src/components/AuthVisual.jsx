export default function AuthVisual() {
  return (
    <div style={{
      position: "relative", background: "linear-gradient(160deg,#0A1E33 0%,#0F3B45 60%,#124A4A 100%)",
      padding: "2.2rem", overflow: "hidden", height: "100%",
      display: "flex", flexDirection: "column", justifyContent: "space-between"
    }}>
      <style>{`
        @keyframes floatA { 0%,100% { transform: translate(0,0); } 50% { transform: translate(6px,-10px); } }
        @keyframes floatB { 0%,100% { transform: translate(0,0); } 50% { transform: translate(-8px,-8px); } }
        @keyframes glowPulse { 0%,100% { opacity: 0.35; } 50% { opacity: 0.6; } }
        @keyframes ekgMove { 0% { stroke-dashoffset: 260; } 100% { stroke-dashoffset: 0; } }
        .f-a { animation: floatA 5s ease-in-out infinite; }
        .f-b { animation: floatB 6s ease-in-out infinite; }
        .glow { animation: glowPulse 4s ease-in-out infinite; }
        .ekg-line { stroke-dasharray: 260; animation: ekgMove 3s linear infinite; }
      `}</style>

      <div className="glow" style={{ position: "absolute", width: 220, height: 220, borderRadius: "50%", background: "#2FB8C4", filter: "blur(55px)", top: 20, left: 40, opacity: 0.4 }} />
      <div className="glow" style={{ position: "absolute", width: 180, height: 180, borderRadius: "50%", background: "#3F8FE0", filter: "blur(50px)", bottom: 30, right: 20, opacity: 0.35, animationDelay: "1.5s" }} />

      <div style={{ position: "relative", color: "white", fontWeight: 500, fontSize: 13, display: "flex", alignItems: "center", gap: 8 }}>
        ArogyaAI — Clinical Triage Network
      </div>

      <div style={{ position: "relative", height: 260 }}>
        <div className="f-a" style={{ position: "absolute", top: 20, left: 30, width: 52, height: 52, background: "rgba(255,255,255,0.08)", border: "1px solid rgba(95,216,204,0.4)", borderRadius: 14 }} />
        <div className="f-b" style={{ position: "absolute", top: 10, right: 20, width: 46, height: 46, background: "rgba(255,255,255,0.08)", border: "1px solid rgba(95,150,216,0.4)", borderRadius: 14 }} />
        <svg viewBox="0 0 320 60" style={{ position: "absolute", bottom: 0, left: 0, width: "100%", height: 60 }}>
          <polyline className="ekg-line" points="0,30 90,30 105,8 120,52 135,15 150,30 320,30" fill="none" stroke="#5FD8CC" strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" />
        </svg>
      </div>

      <div style={{ position: "relative", color: "#BFE3E8", fontSize: 12.5, lineHeight: 1.5 }}>
        Real-time triage, records and emergency guidance — one secure workspace.
      </div>
    </div>
  );
}