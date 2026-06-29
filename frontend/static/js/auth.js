/**
 * ULTRON AI – User Session Management
 */

class Auth {
  static init() {
    const currentPage = window.location.pathname.split('/').pop();

    // Public pages
    const isPublicPage =
      currentPage === "" ||
      currentPage === "index.html" ||
      currentPage === "login.html";

    const token = localStorage.getItem("ultron_token");

    // If user is NOT logged in and trying to access protected pages
    if (!token && !isPublicPage) {
      window.location.href = "login.html";
      return;
    }

    // If already logged in and opens login page
    if (token && currentPage === "login.html") {
      window.location.href = "dashboard.html";
      return;
    }

    // Load recruiter profile
    const user = this.getUser();

    if (user) {
      const avatarEl = document.getElementById("user-avatar-text");
      const nameEl = document.getElementById("user-name-text");

      if (avatarEl) {
        avatarEl.textContent = user.full_name
          ? user.full_name.charAt(0).toUpperCase()
          : "R";
      }

      if (nameEl) {
        nameEl.textContent = user.full_name || "Recruiter";
      }
    }
  }

  static saveSession(token, user) {
    localStorage.setItem("ultron_token", token);
    localStorage.setItem("ultron_user", JSON.stringify(user));
  }

  static logout() {
    localStorage.removeItem("ultron_token");
    localStorage.removeItem("ultron_user");
    localStorage.removeItem("ultron_active_job_id");

    window.location.href = "index.html";
  }

  static getUser() {
    try {
      const user = localStorage.getItem("ultron_user");
      return user ? JSON.parse(user) : null;
    } catch (e) {
      console.error("Invalid user session");
      return null;
    }
  }

  static getActiveJob() {
    return localStorage.getItem("ultron_active_job_id");
  }

  static setActiveJob(jobId) {
    localStorage.setItem("ultron_active_job_id", jobId);
  }
}

// Initialize authentication
document.addEventListener("DOMContentLoaded", () => {
  Auth.init();
});
