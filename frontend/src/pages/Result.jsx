import { useLocation, useNavigate } from "react-router-dom";
import Logo from "../components/Logo";
import Button from "../components/Button";

const ACUITY_STYLES = {
  low: { bg: "#E6F2EA", text: "#2E7D4F", label: "Low urgency" },
  moderate: { bg: "#FBF1DA", text: "#B58900", label: "Moderate urgency" },
  urgent: { bg: "#FCE9DE", text: "#C1531B", label: "Urgent" },
  emergency: { bg: "#FBE4E2", text: "#B3261E", label: "Emergency" }
};

function EmergencyHospitalLink(props) {
  return (
    <a href={props.url} target="_blank" rel="noopener noreferrer" style={{
        display: "block",
        background: "rgba(255,255,255,0.12)",
        borderRadius: 8,
        padding: "10px 12px",
        marginBottom: 6,
        color: "white",
        textDecoration: "none",
        fontSize: 13
      }}>
      <strong>{props.name}</strong> {"\u2014"} {props.distance} km away {"\u2192"}
    </a>
  );
}

function CareLink(props) {
  return (
    <a href={props.url} target="_blank" rel="noopener noreferrer" style={{
        display: "block",
        background: "#F6F7F6",
        borderRadius: 8,
        padding: "10px 12px",
        marginBottom: 6,
        color: "#14191F",
        textDecoration: "none",
        fontSize: 13,
        border: "1px solid #DFE3E6"
      }}>
      <strong>{props.name}</strong> {"\u2014"} {props.distance} km away {"\u2192"}
    </a>
  );
}

export default function Result() {
  const locationData = useLocation();
  const navigate = useNavigate();
  const state = locationData.state;

  if (!state || !state.agentResult) {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <p>No result to show.</p>
        <Button onClick={() => navigate("/symptoms")}>Go back</Button>
      </div>
    );
  }

  const agentResult = state.agentResult;
  const triageLevel = agentResult.triage_level;
  const emergency = agentResult.emergency;
  const style = ACUITY_STYLES[triageLevel] || ACUITY_STYLES.moderate;
  const isEmergency = emergency && emergency.emergency_triggered;
  const nearbyCare = agentResult.nearby_care;

  return (
    <div style={{ minHeight: "100vh", background: "#F6F7F6", padding: "3rem 1rem", display: "flex", justifyContent: "center" }}>
      <div style={{ width: 520 }}>
        <div style={{ marginBottom: 24 }}>
          <Logo />
        </div>

        <div className="acuity-badge" style={{ background: style.bg, color: style.text, marginBottom: 16 }}>
          {style.label.toUpperCase()}
        </div>

        {isEmergency && (
          <div style={{ background: "#B3261E", color: "white", borderRadius: 10, padding: 20, marginBottom: 20 }}>
            <p style={{ fontWeight: 600, fontSize: 16, margin: "0 0 8px" }}>
              {"\u26A0"} This looks like an emergency
            </p>
            <p style={{ fontSize: 13.5, margin: "0 0 14px", lineHeight: 1.5 }}>
              {emergency.message}
            </p>

            <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
              <a href={"tel:" + emergency.ambulance_number} style={{
                  flex: 1,
                  background: "white",
                  color: "#B3261E",
                  textAlign: "center",
                  padding: "10px",
                  borderRadius: 8,
                  fontWeight: 600,
                  textDecoration: "none",
                  fontSize: 14
                }}>
                Call {emergency.ambulance_number} (Ambulance)
              </a>
              <a href={"tel:" + emergency.national_emergency_number} style={{
                  flex: 1,
                  background: "rgba(255,255,255,0.15)",
                  color: "white",
                  textAlign: "center",
                  padding: "10px",
                  borderRadius: 8,
                  fontWeight: 600,
                  textDecoration: "none",
                  fontSize: 14,
                  border: "1px solid white"
                }}>
                Call {emergency.national_emergency_number}
              </a>
            </div>

            {emergency.nearby_hospitals && emergency.nearby_hospitals.length > 0 && (
              <div>
                <p style={{ fontSize: 13, fontWeight: 600, margin: "0 0 8px" }}>Nearest hospitals</p>
                {emergency.nearby_hospitals.map(function (hospital, index) {
                  return (
                    <EmergencyHospitalLink
                      key={index}
                      url={hospital.directions_url}
                      name={hospital.name}
                      distance={hospital.distance_km}
                    />
                  );
                })}
              </div>
            )}
          </div>
        )}

        <div className="card">
          <p style={{ fontSize: 15, fontWeight: 500, margin: "0 0 8px" }}>Possible reasons</p>
          <p style={{ fontSize: 13.5, color: "#4B535C", lineHeight: 1.6, marginBottom: 20 }}>
            {agentResult.reasoning || "A clinician will review this shortly."}
          </p>

          {!isEmergency && agentResult.specialty && (
            <div style={{ marginBottom: 20 }}>
              <p style={{ fontSize: 13, fontWeight: 600, color: "#14191F", marginBottom: 10 }}>
                Recommended: see a {agentResult.specialty}
              </p>

              {nearbyCare && nearbyCare.results && nearbyCare.results.length > 0 ? (
                <div>
                  {!nearbyCare.specialty_match_found && (
                    <p style={{ fontSize: 12, color: "#8A93A0", marginBottom: 8 }}>
                      No exact specialty match found nearby {"\u2014"} showing general hospitals instead.
                    </p>
                  )}
                  {nearbyCare.results.map(function (hospital, index) {
                    return (
                      <CareLink
                        key={index}
                        url={hospital.directions_url}
                        name={hospital.name}
                        distance={hospital.distance_km}
                      />
                    );
                  })}
                </div>
              ) : (
                <p style={{ fontSize: 12.5, color: "#8A93A0" }}>
                  Share your location on the symptoms page to see nearby options.
                </p>
              )}
            </div>
          )}

          {!isEmergency && (
            <Button onClick={() => navigate("/profile-setup", { state: state })}>
              Continue - complete my health profile
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}