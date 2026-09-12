export default function Input({ label, error, icon, ...props }) {
  return (
    <div style={{ marginBottom: 16 }}>
      {label && <label className="block text-xs text-[#4B535C] mb-1.5">{label}</label>}
      <div style={{ position: "relative" }}>
        {icon && (
          <span style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "#8A93A0" }}>
            {icon}
          </span>
        )}
        <input
          className="w-full border border-[#DFE3E6] rounded-lg text-sm outline-none focus:border-[#0F5C56] focus:ring-2 focus:ring-[#0F5C56]/20 transition-shadow"
          style={{ padding: icon ? "10px 12px 10px 36px" : "10px 12px" }}
          {...props}
        />
      </div>
      {error && <p style={{ color: "#B3261E", fontSize: 12, marginTop: 4 }}>{error}</p>}
    </div>
  );
}