import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaStethoscope, FaUser, FaEnvelope, FaLock } from "react-icons/fa";
import axios from "axios";

function Register() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    // Validate
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      // Generate username from email
      const username = email
        .trim()
        .split("@")[0]
        .replace(/[^a-zA-Z0-9_]/g, "");

      const response = await axios.post(
        "http://127.0.0.1:8000/register/",
        {
          full_name: fullName.trim(),
          username: username,
          email: email.trim().toLowerCase(),
          password: password,
        }
      );

      console.log("Registration successful:", response.data);

      // Backend may return tokens after registration
      if (response.data.access) {
        localStorage.setItem("access", response.data.access);
      }

      if (response.data.refresh) {
        localStorage.setItem("refresh", response.data.refresh);
      }

      if (response.data.user) {
        localStorage.setItem(
          "user",
          JSON.stringify(response.data.user)
        );
      }

      // Go to login page
      navigate("/login");

    } catch (err) {
      console.log("Registration error:", err.response?.data || err);

      const data = err.response?.data;

      if (data) {
        if (data.email) {
          setError(
            Array.isArray(data.email)
              ? data.email[0]
              : data.email
          );
        } else if (data.username) {
          setError(
            Array.isArray(data.username)
              ? data.username[0]
              : data.username
          );
        } else if (data.password) {
          setError(
            Array.isArray(data.password)
              ? data.password[0]
              : data.password
          );
        } else if (data.error) {
          setError(data.error);
        } else {
          setError("Registration failed. Please check your details.");
        }
      } else {
        setError("Unable to connect to the server.");
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-brand">
          <div className="brand-icon">
            <FaStethoscope />
          </div>

          <h1>FMT@Fingertips</h1>
          <p>Your Forensic Medicine Assistant</p>
        </div>

        <div className="auth-content">
          <h2>Create Account</h2>

          <p className="auth-subtitle">
            Create your account to start learning with FMT@Fingertips
          </p>

          <form onSubmit={handleSubmit}>

            {/* Full Name */}
            <div className="input-group">
              <label>Full Name</label>

              <div className="input-wrapper">
                <FaUser />

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div className="input-group">
              <label>Email</label>

              <div className="input-wrapper">
                <FaEnvelope />

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div className="input-group">
              <label>Password</label>

              <div className="input-wrapper">
                <FaLock />

                <input
                  type="password"
                  placeholder="Create a password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div className="input-group">
              <label>Confirm Password</label>

              <div className="input-wrapper">
                <FaLock />

                <input
                  type="password"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <p
                style={{
                  color: "#d9534f",
                  fontSize: "13px",
                  marginTop: "8px",
                  marginBottom: "8px",
                }}
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              className="auth-button"
              disabled={loading}
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>

          </form>

          <div className="auth-divider">
            <span>OR</span>
          </div>

          <p className="auth-switch">
            Already have an account?{" "}
            <Link to="/login">Sign In</Link>
          </p>
        </div>

      </div>
    </div>
  );
}

export default Register;