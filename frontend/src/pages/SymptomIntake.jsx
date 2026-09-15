import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Logo from "../components/Logo";
import Button from "../components/Button";

export default function SymptomIntake() {
  const [symptomsText, setSymptomsText] = useState("");
  const [image, setImage] = useState(null);
  const [audio, setAudio] = useState(null);
  const [location, setLocation] = useState({ lat: null, lon: null });
  const [locationStatus, setLocationStatus] = useState("requesting");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    if (!navigator.geolocation) {
      Promise.resolve().then(() => setLocationStatus("unavailable"));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude });
        setLocationStatus("granted");
      },
      () => setLocationStatus("denied")
    );
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const patientRes = await api.post("/patients/", { name: "Self", age: null, gender: null });
      const patientId = patientRes.data.id;

      const caseRes = await api.post("/cases/", {
        patient_id: patientId,
        symptoms_text: symptomsText,
        image_path: null,
        audio_transcript: null,
        latitude: location.lat ? String(location.lat) : null,
        longitude: location.lon ? String(location.lon) : null,
      });
      const caseId = caseRes.data.id;

      const agentRes = await api.post(`/cases/${caseId}/run-agent`);

      navigate("/result", { state: { agentResult: agentRes.data, caseId, patientId } });
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const locationLabel = {
    requesting: "📍 Getting your location...",
    granted: "📍 Location ready — nearby help can be found instantly if needed",
    denied: "📍 Location access denied — enable it for faster emergency help",
    unavailable: "📍 Location not supported on this device",
  }[locationStatus];

  return (
    <div style={{ minHeight: "100vh", background: "#F6F7F6", display: "flex", flexDirection: "column", alignItems: "center", padding: "4rem 1.5rem" }}>
      <div style={{ width: 760 }}>
        <div style={{ marginBottom: 36 }}><Logo /></div>
        <p style={{ fontSize: 26, fontWeight: 500, color: "#14191F", margin: "0 0 8px" }}>What's going on?</p>
        <p style={{ fontSize: 14.5, color: "#4B535C", margin: "0 0 32px", lineHeight: 1.6 }}>
          Describe your symptoms in your own words. If this looks urgent, we'll flag it and show
          you emergency contacts and nearby hospitals right away — you can add your full health
          profile afterward.
        </p>

        <form onSubmit={handleSubmit} className="card" style={{ padding: 32 }}>
          <label style={{ fontSize: 13.5, color: "#4B535C", marginBottom: 8, display: "block", fontWeight: 500 }}>
            Symptoms
          </label>
          <textarea
            value={symptomsText}
            onChange={(e) => setSymptomsText(e.target.value)}
            placeholder="e.g. Sudden chest pain radiating to my left arm, sweating, hard to breathe"
            required
            rows={9}
            style={{
              width: "100%", border: "1px solid #DFE3E6", borderRadius: 10, padding: 16,
              fontSize: 15, fontFamily: "inherit", resize: "vertical", boxSizing: "border-box",
              marginBottom: 20, lineHeight: 1.6
            }}
          />

          <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
            <label style={{ flex: 1, border: "1px dashed #DFE3E6", borderRadius: 10, padding: "14px 16px", fontSize: 13.5, color: "#4B535C", cursor: "pointer", textAlign: "center" }}>
              {image ? `📷 ${image.name}` : "+ Add photo"}
              <input type="file" accept="image/*" style={{ display: "none" }} onChange={(e) => setImage(e.target.files[0])} />
            </label>
            <label style={{ flex: 1, border: "1px dashed #DFE3E6", borderRadius: 10, padding: "14px 16px", fontSize: 13.5, color: "#4B535C", cursor: "pointer", textAlign: "center" }}>
              {audio ? `🎙️ ${audio.name}` : "+ Add voice note"}
              <input type="file" accept="audio/*" style={{ display: "none" }} onChange={(e) => setAudio(e.target.files[0])} />
            </label>
          </div>

          <p style={{
            fontSize: 12.5,
            color: locationStatus === "granted" ? "#2E7D4F" : "#8A93A0",
            marginBottom: 22
          }}>
            {locationLabel}
          </p>

          {error && <p style={{ color: "#B3261E", fontSize: 13.5, marginBottom: 14 }}>{error}</p>}
          <Button type="submit" loading={loading}>Check my symptoms</Button>
        </form>
      </div>
    </div>
  );
}