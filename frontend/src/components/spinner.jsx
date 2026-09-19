export default function Spinner({ size = 20 }) {
  return (
    <>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      <div style={{
        width: size, height: size, border: "2.5px solid #DFE3E6",
        borderTopColor: "#0F5C56", borderRadius: "50%",
        animation: "spin 0.7s linear infinite"
      }} />
    </>
  );
}