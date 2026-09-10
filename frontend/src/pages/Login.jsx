import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaStethoscope, FaEnvelope, FaLock } from "react-icons/fa";
import axios from "axios";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await axios.post(
        "https://fmt-fingertips-backend.onrender.com/login/",
        {
          email: email.trim(),
          password: password,
        }
      );

      console.log("Login response:", response.data);

      // Save JWT access token
      if (response.data.access) {
        localStorage.setItem("access", response.data.access);
      }

      // Save refresh token
      if (response.data.refresh) {
        localStorage.setItem("refresh", response.data.refresh);
      }

      // Save user data if backend sends it
      if (response.data.user) {
        localStorage.setItem(
          "user",
          JSON.stringify(response.data.user)
        );
      }

      navigate("/");
    } catch (error) {
      console.log("Login error:", error.response?.data || error);

      if (error.response?.data?.error) {
        setError(error.response.data.error);
      } else if (error.response?.data?.detail) {
        setError(error.response.data.detail);
      } else {
        setError("Invalid email or password.");
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

          <h2>Welcome Back</h2>

          <p className="auth-subtitle">
            Sign in to continue learning with FMT@Fingertips
          </p>

          <form onSubmit={handleSubmit}>

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

            <div className="input-group">
              <label>Password</label>

              <div className="input-wrapper">
                <FaLock />

                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

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

            <div className="forgot-password">
              <a href="#">Forgot password?</a>
            </div>

            <button
              type="submit"
              className="auth-button"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>

          </form>

          <div className="auth-divider">
            <span>OR</span>
          </div>

          <p className="auth-switch">
            Don't have an account?{" "}
            <Link to="/register">Create Account</Link>
          </p>

        </div>
      </div>
    </div>
  );
}

export default Login;