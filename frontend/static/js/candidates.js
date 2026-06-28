/**
 * ULTRON AI – Candidates Directory Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  Utils.loadSidebar('candidates');

  const container = document.getElementById('candidates-container');
  const searchInput = document.getElementById('search-input');
  const expFilter = document.getElementById('experience-filter');
  const skillInput = document.getElementById('skill-input');
  const filterBtn = document.getElementById('filter-btn');

  let allCandidates = [];

  async function fetchCandidates() {
    try {
      const data = await APIClient.get('/candidates');
      allCandidates = data.candidates || [];
      renderCandidates(allCandidates);
    } catch (error) {
      console.error(error);
      container.innerHTML = `
        <p style="color: var(--text-light); text-align: center; grid-column: span 2; padding: 3rem;">
          Failed to fetch candidate directory. Ensure FastAPI server is running.
        </p>
      `;
    }
  }

  function renderCandidates(candidates) {
    if (candidates.length === 0) {
      container.innerHTML = `
        <p style="color: var(--text-light); text-align: center; grid-column: span 2; padding: 3rem;">
          No candidates found matching the active filters.
        </p>
      `;
      return;
    }

    container.innerHTML = '';
    candidates.forEach(cand => {
      const profile = cand.parsed_profile || {};
      const skills = profile.skills || [];
      const exp = profile.total_experience_years || 0;
      const role = profile.current_role || 'Not specified';
      
      const skillsHtml = skills.slice(0, 5).map(s => `
        <span class="badge badge-primary" style="font-size: 0.75rem;">${s}</span>
      `).join('');

      container.insertAdjacentHTML('beforeend', `
        <div class="card fade-in-up" style="display: flex; flex-direction: column; justify-content: space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
              <div>
                <h3 style="color: var(--primary-color);">${cand.name}</h3>
                <p style="font-weight: bold; font-size: 0.9rem; color: var(--text-dark); margin-top: 0.1rem;">${role}</p>
                <p style="font-size: 0.8rem; color: var(--text-light); margin-top: 0.1rem;">${cand.email || 'No email'}</p>
              </div>
              <span class="badge badge-success">${Utils.getExperienceText(exp)}</span>
            </div>
            
            <p style="font-size: 0.85rem; color: var(--text-dark); margin-bottom: 1.5rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
              ${profile.summary || 'No summary available.'}
            </p>
          </div>
          
          <div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1.5rem;">
              ${skillsHtml}
              ${skills.length > 5 ? `<span style="font-size: 0.75rem; color: var(--text-light); align-self: center;">+${skills.length - 5} more</span>` : ''}
            </div>
            
            <div style="display: flex; gap: 1rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
              <a href="candidate-detail.html?id=${cand.id}" class="btn btn-secondary" style="flex-grow: 1; font-size: 0.8rem; padding: 0.5rem 1rem;">View Profile</a>
              <a href="chat.html?session=default&query=Tell me about ${cand.name}" class="btn btn-accent" style="font-size: 0.8rem; padding: 0.5rem 1rem;">Chat AI</a>
            </div>
          </div>
        </div>
      `);
    });
  }

  // Filter application logic
  function applyFilters() {
    const q = searchInput.value.toLowerCase().trim();
    const exp = expFilter.value;
    const skill = skillInput.value.toLowerCase().trim();

    let filtered = allCandidates;

    if (q) {
      filtered = filtered.filter(c => 
        c.name.toLowerCase().includes(q) || 
        (c.parsed_profile?.current_role || '').toLowerCase().includes(q) ||
        (c.email || '').toLowerCase().includes(q)
      );
    }

    if (exp !== 'all') {
      filtered = filtered.filter(c => {
        const years = c.parsed_profile?.total_experience_years || 0;
        if (exp === 'junior') return years <= 2;
        if (exp === 'mid') return years > 2 && years <= 5;
        if (exp === 'senior') return years > 5;
        return true;
      });
    }

    if (skill) {
      filtered = filtered.filter(c => {
        const skills = (c.parsed_profile?.skills || []).map(s => s.toLowerCase());
        const techSkills = (c.parsed_profile?.technical_skills || []).map(s => s.toLowerCase());
        return skills.some(s => s.includes(skill)) || techSkills.some(s => s.includes(skill));
      });
    }

    renderCandidates(filtered);
  }

  filterBtn.addEventListener('click', applyFilters);
  searchInput.addEventListener('input', applyFilters);

  // Initialize
  fetchCandidates();
});
