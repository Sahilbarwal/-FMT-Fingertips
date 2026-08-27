import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaBookMedical,
  FaArrowLeft,
  FaUserCircle,
  FaEnvelope,
  FaCalendarAlt,
  FaSignOutAlt,
  FaHistory,
} from "react-icons/fa";
import axios from "axios";

function Profile() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      navigate("/login");
      return;
    }

    axios
      .get("http://127.0.0.1:8000/me/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {
        console.log("Profile data:", response.data);
        setUser(response.data);
      })
      .catch((error) => {
        console.log("Profile error:", error);

        if (error.response?.status === 401) {
          localStorage.removeItem("access");
          navigate("/login");
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("access");
    navigate("/login");
  };

  if (loading) {
    return <div>Loading profile...</div>;
  }

  if (!user) {
    return null;
  }

  return (
    <div className="profile-page">

      {/* Navbar */}
      <nav className="profile-navbar">

        <div className="profile-brand">

          <div className="profile-brand-icon">
            <FaBookMedical />
          </div>

          <div>
            <h2>FMT@Fingertips</h2>
            <span>Forensic Medicine Assistant</span>
          </div>

        </div>

        <button
          className="profile-history-button"
          onClick={() => navigate("/history")}
        >
          <FaHistory />
          History
        </button>

      </nav>

      {/* Main */}
      <main className="profile-container">

        <button
          className="profile-back"
          onClick={() => navigate("/")}
        >
          <FaArrowLeft />
          Back to Home
        </button>

        <div className="profile-card">

          {/* Profile Header */}
          <div className="profile-header">

            <div className="profile-avatar">
              <FaUserCircle />
            </div>

            <div>
              <h1>{user.username}</h1>
              <p>{user.email}</p>
            </div>

          </div>

          {/* Account Information */}
          <div className="profile-section">

            <h2>Account Information</h2>

            <div className="profile-info">

              <div className="profile-info-item">

                <div className="profile-info-icon">
                  <FaUserCircle />
                </div>

                <div>
                  <span>Username</span>
                  <strong>{user.username}</strong>
                </div>

              </div>

              <div className="profile-info-item">

                <div className="profile-info-icon">
                  <FaEnvelope />
                </div>

                <div>
                  <span>Email</span>
                  <strong>{user.email}</strong>
                </div>

              </div>

              <div className="profile-info-item">

                <div className="profile-info-icon">
                  <FaCalendarAlt />
                </div>

                <div>
                  <span>Account ID</span>
                  <strong>{user.id}</strong>
                </div>

              </div>

            </div>

          </div>

          {/* Quick Actions */}
          <div className="profile-section">

            <h2>Quick Actions</h2>

            <button
              className="profile-action"
              onClick={() => navigate("/history")}
            >
              <div>
                <FaHistory />
              </div>

              <span>View Search History</span>
            </button>

          </div>

          {/* Logout */}
          <button
            className="logout-button"
            onClick={handleLogout}
          >
            <FaSignOutAlt />
            Logout
          </button>

        </div>

        <p className="profile-footer">
          FMT@Fingertips • Your Forensic Medicine Learning Assistant
        </p>

      </main>

    </div>
  );
}

export default Profile;