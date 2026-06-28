/**
 * ULTRON AI – User Session Management
 */

class Auth {
  static init() {
    // Check auth on secure pages
    const isPublicPage = window.location.pathname.endsWith('login.html') || 
                         window.location.pathname.endsWith('index.html') ||
                         window.location.pathname === '/';
    
    const token = localStorage.getItem('ultron_token');
    
    if (!token && !isPublicPage) {
      window.location.href = 'login.html';
    }

    if (token && isPublicPage && window.location.pathname.endsWith('login.html')) {
      window.location.href = 'dashboard.html';
    }

    // Set user profile info if element exists
    const user = this.getUser();
    if (user) {
      const avatarEl = document.getElementById('user-avatar-text');
      const nameEl = document.getElementById('user-name-text');
      if (avatarEl) avatarEl.textContent = user.full_name ? user.full_name.charAt(0).toUpperCase() : 'R';
      if (nameEl) nameEl.textContent = user.full_name || 'Recruiter';
    }
  }

  static saveSession(token, user) {
    localStorage.setItem('ultron_token', token);
    localStorage.setItem('ultron_user', JSON.stringify(user));
  }

  static logout() {
    localStorage.removeItem('ultron_token');
    localStorage.removeItem('ultron_user');
    window.location.href = 'index.html';
  }

  static getUser() {
    const userStr = localStorage.getItem('ultron_user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  }

  static getActiveJob() {
    return localStorage.getItem('ultron_active_job_id');
  }

  static setActiveJob(jobId) {
    localStorage.setItem('ultron_active_job_id', jobId);
  }
}

// Auto run auth check on load
document.addEventListener('DOMContentLoaded', () => Auth.init());
