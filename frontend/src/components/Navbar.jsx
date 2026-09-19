import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import Logo from "./Logo";

export default function Navbar() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    localStorage.removeItem("patientId");
    navigate("/login");
  };

  return (
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      padding: "16px 32px", background: "white", borderBottom: "1px solid #DFE3E6"
    }}>
      <Logo />
      <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
        <span
          style={{ fontSize: 13, color: "#4B535C", cursor: "pointer" }}
          onClick={() => navigate("/symptoms")}
        >
          + New check-in
        </span>
        <span
          style={{ fontSize: 13, color: "#B3261E", cursor: "pointer" }}
          onClick={handleLogout}
        >
          Logout
        </span>
      </div>
    </div>
  );
}