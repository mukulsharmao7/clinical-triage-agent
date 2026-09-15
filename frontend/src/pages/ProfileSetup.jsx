import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../services/api";
import Logo from "../components/Logo";
import Button from "../components/Button";
import Input from "../components/Input";

export default function ProfileSetup() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const patientId = state?.patientId;

  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState({
    chronic_conditions: "", allergies: "", current_medications: "",
    blood_group: "", emergency_contact_name: "", emergency_contact_phone: ""
  });
  const [insurance, setInsurance] = useState({ provider_name: "", policy_number: "", coverage_amount: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateProfile = (key) => (e) => setProfile({ ...profile, [key]: e.target.value });
  const updateInsurance = (key) => (e) => setInsurance({ ...insurance, [key]: e.target.value });

  const handleFinish = async () => {
    setError("");
    setLoading(true);
    try {
      await api.post("/patient-profile/", { patient_id: patientId, ...profile });

      if (insurance.provider_name && insurance.policy_number) {
        await api.post("/insurance/policies", {
          patient_id: patientId,
          provider_name: insurance.provider_name,
          policy_number: insurance.policy_number,
          coverage_amount: insurance.coverage_amount ? parseInt(insurance.coverage_amount) : null,
        });
      }

      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!patientId) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <p>No patient context found.</p>
        <Button onClick={() => navigate("/symptoms")}>Start over</Button>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#F6F7F6", display: "flex", flexDirection: "column", alignItems: "center", padding: "3rem 1.5rem" }}>
      <div style={{ width: 560 }}>
        <div style={{ marginBottom: 28 }}><Logo /></div>

        <div style={{ display: "flex", gap: 6, marginBottom: 24 }}>
          {[1, 2].map((s) => (
            <div key={s} style={{
              flex: 1, height: 4, borderRadius: 2,
              background: s <= step ? "#0F5C56" : "#DFE3E6"
            }} />
          ))}
        </div>

        {step === 1 && (
          <div className="card">
            <p style={{ fontSize: 18, fontWeight: 500, margin: "0 0 4px" }}>Your health background</p>
            <p style={{ fontSize: 13, color: "#4B535C", margin: "0 0 20px" }}>
              This helps us give you more accurate guidance in the future.
            </p>

            <Input label="Chronic conditions (if any)" value={profile.chronic_conditions} onChange={updateProfile("chronic_conditions")} placeholder="e.g. Hypertension, Diabetes" />
            <Input label="Allergies (if any)" value={profile.allergies} onChange={updateProfile("allergies")} placeholder="e.g. Penicillin" />
            <Input label="Current medications" value={profile.current_medications} onChange={updateProfile("current_medications")} placeholder="e.g. Metformin 500mg" />
            <Input label="Blood group" value={profile.blood_group} onChange={updateProfile("blood_group")} placeholder="e.g. O+" />
            <Input label="Emergency contact name" value={profile.emergency_contact_name} onChange={updateProfile("emergency_contact_name")} placeholder="Full name" />
            <Input label="Emergency contact phone" value={profile.emergency_contact_phone} onChange={updateProfile("emergency_contact_phone")} placeholder="10-digit number" />

            <Button onClick={() => setStep(2)}>Continue</Button>
          </div>
        )}

        {step === 2 && (
          <div className="card">
            <p style={{ fontSize: 18, fontWeight: 500, margin: "0 0 4px" }}>Insurance (optional)</p>
            <p style={{ fontSize: 13, color: "#8A93A0", margin: "0 0 20px" }}>
              Demo data only — for illustration purposes.
            </p>

            <Input label="Provider name" value={insurance.provider_name} onChange={updateInsurance("provider_name")} placeholder="e.g. Star Health" />
            <Input label="Policy number" value={insurance.policy_number} onChange={updateInsurance("policy_number")} placeholder="e.g. SH12345" />
            <Input label="Coverage amount (₹)" type="number" value={insurance.coverage_amount} onChange={updateInsurance("coverage_amount")} placeholder="e.g. 500000" />

            {error && <p style={{ color: "#B3261E", fontSize: 13, marginBottom: 12 }}>{error}</p>}

            <div style={{ display: "flex", gap: 10 }}>
              <Button variant="secondary" onClick={() => setStep(1)}>Back</Button>
              <Button loading={loading} onClick={handleFinish}>Finish setup</Button>
            </div>
          </div>
        )}

        <p style={{ fontSize: 12.5, color: "#8A93A0", textAlign: "center", marginTop: 16 }}>
          <span style={{ cursor: "pointer", textDecoration: "underline" }} onClick={() => navigate("/dashboard")}>
            Skip for now
          </span>
        </p>
      </div>
    </div>
  );
}