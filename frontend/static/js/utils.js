/**
 * ULTRON AI – UI Helpers
 */

class Utils {
  static formatDate(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }

  static formatScore(score) {
    if (score === undefined || score === null) return '0%';
    return `${parseFloat(score).toFixed(0)}%`;
  }

  static getScoreClass(score) {
    if (score >= 80) return 'high';
    if (score >= 50) return 'mid';
    return 'low';
  }

  static getExperienceText(years) {
    if (!years) return 'Fresher';
    if (years === 1) return '1 year';
    return `${years} years`;
  }

  static getBadgeClass(status) {
    const statuses = {
      'active': 'badge-success',
      'closed': 'badge-danger',
      'pending': 'badge-warning',
      'default': 'badge-primary'
    };
    return statuses[status.toLowerCase()] || statuses['default'];
  }

  static loadSidebar(activeId) {
    const sidebarHtml = `
      <div class="sidebar">
        <a href="dashboard.html" class="sidebar-logo">
          <span class="brand-title" style="color: var(--primary-color);">ULTRON AI</span>
        </a>
        <ul class="nav-links">
          <li class="nav-item ${activeId === 'dashboard' ? 'active' : ''}">
            <a href="dashboard.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" /></svg>
              Dashboard
            </a>
          </li>
          <li class="nav-item ${activeId === 'upload-job' ? 'active' : ''}">
            <a href="upload-job.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
              Upload Job (JD)
            </a>
          </li>
          <li class="nav-item ${activeId === 'upload-resume' ? 'active' : ''}">
            <a href="upload-resume.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" /></svg>
              Upload Resumes
            </a>
          </li>
          <li class="nav-item ${activeId === 'candidates' ? 'active' : ''}">
            <a href="candidates.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.109A11.386 11.386 0 0 1 10.089 21c-2.243 0-4.32-.647-6.08-1.764v-.135a3 3 0 0 1 3-3h3a3 3 0 0 1 3 3v.109M4.5 19.5v.005c0-1.114.285-2.16.786-3.07M11.25 11.25a3.375 3.375 0 1 0 0-6.75 3.375 3.375 0 0 0 0 6.75ZM12 1.625a3 3 0 1 0 0 6 3 3 0 0 0 0-6ZM18.75 12.375a2.625 2.625 0 1 0 0-5.25 2.625 2.625 0 0 0 0 5.25ZM19.5 5.625a2.25 2.25 0 1 0 0 4.5 2.25 2.25 0 0 0 0-4.5Z" /></svg>
              Candidates List
            </a>
          </li>
          <li class="nav-item ${activeId === 'rankings' ? 'active' : ''}">
            <a href="rankings.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v5.25c0 .621-.504 1.125-1.125 1.125h-2.25A1.125 1.125 0 0 1 3 18.375v-5.25ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125v-9.75ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v14.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" /></svg>
              AI Rankings
            </a>
          </li>
          <li class="nav-item ${activeId === 'analytics' ? 'active' : ''}">
            <a href="analytics.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" /></svg>
              Analytics
            </a>
          </li>
          <li class="nav-item ${activeId === 'chat' ? 'active' : ''}">
            <a href="chat.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" /></svg>
              AI Recruiter Assistant
            </a>
          </li>
          <li class="nav-item ${activeId === 'settings' ? 'active' : ''}">
            <a href="settings.html">
              <svg fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.43l-1.003.828c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.43l1.004-.827c.292-.24.437-.613.43-.991a6.936 6.936 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" /></svg>
              Settings
            </a>
          </li>
        </ul>
        <div class="sidebar-footer">
          <div class="user-profile-menu">
            <div class="user-avatar" id="user-avatar-text">R</div>
            <div>
              <div style="font-weight: 600;" id="user-name-text">Recruiter</div>
              <a href="#" onclick="Auth.logout()" style="color: var(--primary-color); font-size: 0.75rem; text-decoration: none;">Log Out</a>
            </div>
          </div>
        </div>
      </div>
    `;
    const container = document.querySelector('.app-container');
    if (container) {
      container.insertAdjacentHTML('afterbegin', sidebarHtml);
    }
  }

  static showError(message) {
    alert(`Error: ${message}`);
  }
}
