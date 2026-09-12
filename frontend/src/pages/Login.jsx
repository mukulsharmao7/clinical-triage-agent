import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";
import { useAuth } from "../context/useAuth";
import AuthVisual from "../components/AuthVisual";
import Logo from "../components/Logo";
import Button from "../components/Button";
import Input from "../components/Input";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await api.post(`/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`);
      login(res.data.access_token);
      navigate("/symptoms");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", minHeight: "100vh" }}>
      <AuthVisual />
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <div style={{ width: 340 }}>
          <div style={{ marginBottom: 32 }}><Logo /></div>
          <p style={{ fontSize: 20, fontWeight: 500, color: "#14191F", margin: "0 0 4px" }}>Sign in</p>
          <p style={{ fontSize: 13, color: "#4B535C", margin: "0 0 24px" }}>Access your secure health workspace.</p>

          <form onSubmit={handleSubmit}>
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required />
            {error && <p style={{ color: "#B3261E", fontSize: 13, marginBottom: 12 }}>{error}</p>}
            <Button type="submit" loading={loading}>Sign in</Button>
          </form>

          <p style={{ fontSize: 13, color: "#4B535C", marginTop: 16, textAlign: "center" }}>
            New here? <Link to="/signup" style={{ color: "#0F5C56", fontWeight: 500 }}>Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}