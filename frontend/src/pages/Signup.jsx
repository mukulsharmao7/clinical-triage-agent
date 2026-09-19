import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/useAuth";
import AuthVisual from "../components/AuthVisual";
import Logo from "../components/Logo";
import Button from "../components/Button";
import Input from "../components/Input";

export default function Signup() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/signup", form);
      const loginRes = await api.post(
        `/auth/login?email=${encodeURIComponent(form.email)}&password=${encodeURIComponent(form.password)}`
      );
      login(loginRes.data.access_token);
      navigate("/symptoms");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", minHeight: "100vh" }}>
      <div className="hide-on-mobile"><AuthVisual /></div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <div style={{ width: 340, maxWidth: "100%" }}>
          <div style={{ marginBottom: 32 }}><Logo /></div>
          <p style={{ fontSize: 20, fontWeight: 500, color: "#14191F", margin: "0 0 4px" }}>Create account</p>
          <p style={{ fontSize: 13, color: "#4B535C", margin: "0 0 24px" }}>Set up your ArogyaAI workspace.</p>

          <form onSubmit={handleSubmit}>
            <Input label="Full name" value={form.full_name} onChange={update("full_name")} placeholder="Your name" required />
            <Input label="Email" type="email" value={form.email} onChange={update("email")} placeholder="you@example.com" required />
            <Input label="Password" type="password" value={form.password} onChange={update("password")} placeholder="Minimum 8 characters" required minLength={8} />
            {error && <p style={{ color: "#B3261E", fontSize: 13, marginBottom: 12 }}>{error}</p>}
            <Button type="submit" loading={loading}>Create account</Button>
          </form>

          <p style={{ fontSize: 13, color: "#4B535C", marginTop: 16, textAlign: "center" }}>
            Already have an account? <Link to="/login" style={{ color: "#0F5C56", fontWeight: 500 }}>Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}