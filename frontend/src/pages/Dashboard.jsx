import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Navbar from "../components/Navbar";

function Section({ title, children, action }) {
  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <p style={{ fontSize: 15, fontWeight: 500, margin: 0 }}>{title}</p>
        {action}
      </div>
      {children}
    </div>
  );
}

function EmptyState({ text }) {
  return <p style={{ fontSize: 13, color: "#8A93A0", margin: 0 }}>{text}</p>;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const patientId = localStorage.getItem("patientId");

  const [profile, setProfile] = useState(null);
  const [policies, setPolicies] = useState([]);
  const [hospitalizations, setHospitalizations] = useState([]);
  const [dietPlan, setDietPlan] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(Boolean(patientId));

  useEffect(() => {
    if (!patientId) {
      return;
    }

    const loadAll = async () => {
      const results = await Promise.allSettled([
        api.get(`/patient-profile/${patientId}`),
        api.get(`/insurance/policies?patient_id=${patientId}`),
        api.get(`/hospitalizations/?patient_id=${patientId}`),
        api.get(`/diet-plan/${patientId}`),
        api.get(`/documents/?patient_id=${patientId}`),
      ]);

      if (results[0].status === "fulfilled") setProfile(results[0].value.data);
      if (results[1].status === "fulfilled") setPolicies(results[1].value.data);
      if (results[2].status === "fulfilled") setHospitalizations(results[2].value.data);
      if (results[3].status === "fulfilled") setDietPlan(results[3].value.data);
      if (results[4].status === "fulfilled") setDocuments(results[4].value.data);

      setLoading(false);
    };

    loadAll();
  }, [patientId]);

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !patientId) return;

    const formData = new FormData();
    formData.append("patient_id", patientId);
    formData.append("document_type", "general");
    formData.append("file", file);

    try {
      await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const res = await api.get(`/documents/?patient_id=${patientId}`);
      setDocuments(res.data);
    } catch {
      // silently ignore for now — could add error toast later
    }
  };

  if (!patientId) {
    return (
      <div>
        <Navbar />
        <div style={{ padding: 60, textAlign: "center" }}>
          <p style={{ fontSize: 16, color: "#4B535C", marginBottom: 16 }}>
            No health record found yet. Start with a symptom check-in.
          </p>
          <button className="btn-primary" onClick={() => navigate("/symptoms")}>
            Start check-in
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div>
        <Navbar />
        <div style={{ padding: 60, textAlign: "center", color: "#8A93A0" }}>Loading your dashboard...</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "#F6F7F6" }}>
      <Navbar />
      <div style={{ maxWidth: 800, margin: "0 auto", padding: "32px 20px" }}>
        <p style={{ fontSize: 22, fontWeight: 500, color: "#14191F", marginBottom: 24 }}>
          Your health dashboard
        </p>

        <Section title="Health profile">
          {profile ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 13.5 }}>
              <div><span style={{ color: "#8A93A0" }}>Blood group:</span> {profile.blood_group || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Chronic conditions:</span> {profile.chronic_conditions || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Allergies:</span> {profile.allergies || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Medications:</span> {profile.current_medications || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Emergency contact:</span> {profile.emergency_contact_name || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Contact phone:</span> {profile.emergency_contact_phone || "—"}</div>
            </div>
          ) : (
            <EmptyState text="No profile set up yet. Complete a check-in to add one." />
          )}
        </Section>

        <Section title="Insurance (demo data)">
          {policies.length > 0 ? (
            policies.map((p) => (
              <div key={p.id} style={{ padding: "10px 0", borderBottom: "1px solid #F0F1F1", fontSize: 13.5 }}>
                <strong>{p.provider_name}</strong> — Policy #{p.policy_number}
                {p.coverage_amount && <span style={{ color: "#8A93A0" }}> · ₹{p.coverage_amount.toLocaleString()} coverage</span>}
              </div>
            ))
          ) : (
            <EmptyState text="No insurance policy on record." />
          )}
        </Section>

        <Section title="Hospitalization history">
          {hospitalizations.length > 0 ? (
            hospitalizations.map((h) => (
              <div key={h.id} style={{ padding: "10px 0", borderBottom: "1px solid #F0F1F1", fontSize: 13.5 }}>
                <strong>{h.hospital_name}</strong> — {h.diagnosis}
                <div style={{ color: "#8A93A0", fontSize: 12, marginTop: 2 }}>
                  {new Date(h.admission_date).toLocaleDateString()}
                  {h.discharge_date && ` – ${new Date(h.discharge_date).toLocaleDateString()}`}
                </div>
              </div>
            ))
          ) : (
            <EmptyState text="No past hospitalizations on record." />
          )}
        </Section>

        <Section title="Diet & lifestyle">
          {dietPlan ? (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 13.5 }}>
              <div><span style={{ color: "#8A93A0" }}>Diet type:</span> {dietPlan.diet_type || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Activity level:</span> {dietPlan.activity_level || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Daily calories:</span> {dietPlan.daily_calorie_target || "—"}</div>
              <div><span style={{ color: "#8A93A0" }}>Avg sleep:</span> {dietPlan.sleep_hours_avg ? `${dietPlan.sleep_hours_avg} hrs` : "—"}</div>
            </div>
          ) : (
            <EmptyState text="No diet or lifestyle info on record." />
          )}
        </Section>

        <Section
          title="Documents"
          action={
            <label style={{ fontSize: 12.5, color: "#0F5C56", cursor: "pointer", fontWeight: 500 }}>
              + Upload
              <input type="file" style={{ display: "none" }} onChange={handleDocumentUpload} />
            </label>
          }
        >
          {documents.length > 0 ? (
            documents.map((d) => (
              <div key={d.id} style={{ padding: "8px 0", borderBottom: "1px solid #F0F1F1", fontSize: 13.5 }}>
                📄 {d.file_path.split(/[\\/]/).pop()} <span style={{ color: "#8A93A0", fontSize: 12 }}>({d.document_type})</span>
              </div>
            ))
          ) : (
            <EmptyState text="No documents uploaded yet." />
          )}
        </Section>
      </div>
    </div>
  );
}