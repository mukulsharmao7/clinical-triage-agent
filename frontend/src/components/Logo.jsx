export default function Logo({ light = false }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{
        width: 28, height: 28, borderRadius: 7,
        background: light ? "rgba(255,255,255,0.15)" : "#0F5C56",
        display: "flex", alignItems: "center", justifyContent: "center"
      }}>
        <span style={{ color: light ? "#5FD8CC" : "white", fontWeight: 700, fontSize: 14 }}>A</span>
      </div>
      <span style={{ fontWeight: 500, fontSize: 14, color: light ? "white" : "#14191F" }}>
        ArogyaAI
      </span>
    </div>
  );
}