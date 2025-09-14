import React, { useState, useEffect } from "react";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState("inspector");
  const [token, setToken] = useState("");
  const [image, setImage] = useState(null);
  const [location, setLocation] = useState("");
  const [fittingType, setFittingType] = useState("");
  const [remarks, setRemarks] = useState("");
  const [message, setMessage] = useState("");
  const [defects, setDefects] = useState([]);
  const [stats, setStats] = useState(null);
  const [showRegister, setShowRegister] = useState(false);

  const API_BASE = "http://localhost:5000";

  // Register new user
  const register = async () => {
    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage("Registration successful! Please login.");
        setShowRegister(false);
      } else {
        setMessage(data.msg || "Registration failed");
      }
    } catch (err) {
      setMessage("Registration failed");
    }
  };

  // Login user
  const login = async () => {
    try {
      const res = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (data.access_token) {
        setToken(data.access_token);
        setMessage("Login successful");
        fetchDefects(data.access_token);
        fetchStats(data.access_token);
      } else {
        setMessage(data.msg || "Login failed");
      }
    } catch (err) {
      setMessage("Login failed");
    }
  };

  // Upload defect data
  const uploadDefect = async () => {
    if (!token) {
      setMessage("Please login first");
      return;
    }
    if (!image) {
      setMessage("Please select an image");
      return;
    }
    try {
      const formData = new FormData();
      formData.append("image", image);
      formData.append("location", location);
      formData.append("fitting_type", fittingType);
      formData.append("remarks", remarks);

      const res = await fetch(`${API_BASE}/defect/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();
      setMessage(data.result ? `Defect uploaded: ${data.result}` : data.msg || "Upload failed");
      
      if (data.result) {
        fetchDefects(token);
        fetchStats(token);
        setImage(null);
        setLocation("");
        setFittingType("");
        setRemarks("");
      }
    } catch (err) {
      setMessage("Upload failed");
    }
  };

  // Fetch all defects
  const fetchDefects = async (authToken) => {
    const tokenToUse = authToken || token;
    if (!tokenToUse) return;
    try {
      const res = await fetch(`${API_BASE}/defects`, {
        headers: { Authorization: `Bearer ${tokenToUse}` },
      });
      const data = await res.json();
      setDefects(data.defects || []);
    } catch (err) {
      console.error("Failed to fetch defects");
    }
  };

  // Fetch user statistics
  const fetchStats = async (authToken) => {
    const tokenToUse = authToken || token;
    if (!tokenToUse) return;
    try {
      const res = await fetch(`${API_BASE}/stats`, {
        headers: { Authorization: `Bearer ${tokenToUse}` },
      });
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch statistics");
    }
  };

  useEffect(() => {
    if (token) {
      fetchDefects(token);
      fetchStats(token);
    }
  }, [token]);

  if (!token) {
    return (
      <div style={{ maxWidth: 400, margin: "auto", padding: 20 }}>
        <h2>Railway Defect Detection</h2>
        
        <div style={{ marginBottom: 20 }}>
          <button onClick={() => setShowRegister(!showRegister)}>
            {showRegister ? "Switch to Login" : "Need an Account? Register"}
          </button>
        </div>

        {showRegister && (
          <>
            <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
            <select value={role} onChange={e => setRole(e.target.value)}>
              <option value="inspector">Inspector</option>
              <option value="engineer">Engineer</option>
              <option value="supervisor">Supervisor</option>
            </select>
          </>
        )}
        
        <input placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
        
        <button onClick={showRegister ? register : login}>
          {showRegister ? "Register" : "Login"}
        </button>

        <p>{message}</p>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "auto", padding: 20 }}>
      <h2>Upload Defect</h2>
      <input type="file" onChange={e => setImage(e.target.files[0])} />
      <input placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
      <input placeholder="Fitting Type" value={fittingType} onChange={e => setFittingType(e.target.value)} />
      <input placeholder="Remarks (optional)" value={remarks} onChange={e => setRemarks(e.target.value)} />
      <button onClick={uploadDefect}>Upload Defect</button>

      <h2>Your Defect Records ({defects.length})</h2>
      <button onClick={() => fetchDefects(token)}>Refresh List</button>
      
      <div style={{ maxHeight: 300, overflowY: 'scroll', border: '1px solid #ccc', padding: 10 }}>
        {defects.map(defect => (
          <div key={defect._id} style={{ border: '1px solid #eee', margin: 5, padding: 10 }}>
            <strong>Location:</strong> {defect.location}<br/>
            <strong>Type:</strong> {defect.fitting_type}<br/>
            <strong>Classification:</strong> {defect.classification}<br/>
            <strong>Date:</strong> {new Date(defect.timestamp).toLocaleString()}<br/>
            {defect.remarks && <><strong>Remarks:</strong> {defect.remarks}<br/></>}
          </div>
        ))}
      </div>

      {stats && (
        <div>
          <h2>Statistics</h2>
          <p><strong>Total Defects:</strong> {stats.total_defects}</p>
          <p><strong>By Type:</strong> {stats.by_type.map(item => `${item._id}: ${item.count}`).join(', ')}</p>
          <p><strong>By Location:</strong> {stats.by_location.map(item => `${item._id}: ${item.count}`).join(', ')}</p>
        </div>
      )}

      <p>{message}</p>
      <button onClick={() => setToken("")}>Logout</button>
    </div>
  );
}

export default App;
