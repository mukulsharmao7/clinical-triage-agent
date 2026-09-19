import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 60, textAlign: "center", fontFamily: "IBM Plex Sans, sans-serif" }}>
          <p style={{ fontSize: 18, fontWeight: 500, marginBottom: 8 }}>Something went wrong</p>
          <p style={{ fontSize: 13.5, color: "#4B535C", marginBottom: 20 }}>
            Please refresh the page. If this keeps happening, contact support.
          </p>
          <button className="btn-primary" style={{ width: "auto", padding: "10px 20px" }} onClick={() => window.location.href = "/login"}>
            Back to login
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}