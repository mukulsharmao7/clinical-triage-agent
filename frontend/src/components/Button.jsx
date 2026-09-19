import Spinner from "./spinner";

export default function Button({ children, loading, variant = "primary", ...props }) {
  const base = "w-full py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed";
  const styles = variant === "primary"
    ? "bg-[#0F5C56] text-white hover:bg-[#0C4A45]"
    : "bg-white text-[#14191F] border border-[#DFE3E6] hover:border-[#0F5C56]";
  return (
    <button className={`${base} ${styles}`} disabled={loading} {...props}>
      {loading && <Spinner size={16} />}
      {loading ? "Please wait..." : children}
    </button>
  );
}