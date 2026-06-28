/**
 * ULTRON AI – Dashboard Controllers
 */

document.addEventListener('DOMContentLoaded', async () => {
  // Load sidebar element
  Utils.loadSidebar('dashboard');

  const kpiJobs = document.getElementById('kpi-jobs');
  const kpiCandidates = document.getElementById('kpi-candidates');
  const kpiMatches = document.getElementById('kpi-matches');
  const kpiAvgScore = document.getElementById('kpi-avg-score');

  const insightsList = document.getElementById('ai-insights-list');
  const topMatchesList = document.getElementById('top-matches-list');
  const recentTable = document.getElementById('recent-resumes-table');

  try {
    const data = await APIClient.get('/dashboard');

    // 1. Set KPIs
    kpiJobs.textContent = data.kpis.total_jobs;
    kpiCandidates.textContent = data.kpis.total_candidates;
    kpiMatches.textContent = data.kpis.matches_analyzed;
    kpiAvgScore.textContent = data.kpis.average_match_score > 0 
      ? `${data.kpis.average_match_score}%` 
      : 'N/A';

    // Set first job as active job if nothing is set
    if (data.recent_jobs && data.recent_jobs.length > 0 && !Auth.getActiveJob()) {
      Auth.setActiveJob(data.recent_jobs[0].id);
    }

    // 2. Set AI Insights
    insightsList.innerHTML = '';
    if (data.ai_insights && data.ai_insights.length > 0) {
      data.ai_insights.forEach(insight => {
        insightsList.insertAdjacentHTML('beforeend', `
          <div style="display: flex; gap: 0.75rem; align-items: flex-start; padding: 0.5rem 0;">
            <span style="font-size: 1.2rem;">💡</span>
            <p style="font-size: 0.95rem; color: var(--text-dark);">${insight}</p>
          </div>
        `);
      });
    } else {
      insightsList.innerHTML = '<p style="color: var(--text-light);">No insights available yet.</p>';
    }

    // 3. Set Top Matches
    topMatchesList.innerHTML = '';
    if (data.top_matches && data.top_matches.length > 0) {
      data.top_matches.forEach(match => {
        const scoreClass = Utils.getScoreClass(match.match_score);
        topMatchesList.insertAdjacentHTML('beforeend', `
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem; margin-bottom: 0.75rem;">
            <div>
              <a href="candidate-detail.html?id=${match.candidate_id}&job_id=${match.job_id}" style="font-weight: bold; color: var(--text-dark); text-decoration: none;">${match.candidate_name}</a>
              <div style="font-size: 0.8rem; color: var(--text-light);">${match.job_title}</div>
            </div>
            <div class="score-badge ${scoreClass}">${match.match_score.toFixed(0)}%</div>
          </div>
        `);
      });
    } else {
      topMatchesList.innerHTML = `
        <div style="text-align: center; padding: 1.5rem 0; color: var(--text-light);">
          <p>No matching candidate data yet.</p>
          <a href="upload-job.html" class="btn btn-accent" style="margin-top: 1rem; font-size: 0.8rem;">Upload Job Description</a>
        </div>
      `;
    }

    // 4. Set Recent Candidates
    recentTable.innerHTML = '';
    if (data.recent_resumes && data.recent_resumes.length > 0) {
      data.recent_resumes.forEach(candidate => {
        recentTable.insertAdjacentHTML('beforeend', `
          <tr>
            <td><a href="candidate-detail.html?id=${candidate.id}" style="font-weight: bold; color: var(--text-dark); text-decoration: none;">${candidate.name}</a></td>
            <td>${candidate.email || 'N/A'}</td>
            <td>${candidate.role}</td>
            <td>${Utils.getExperienceText(candidate.experience)}</td>
            <td>${Utils.formatDate(candidate.uploaded_at)}</td>
          </tr>
        `);
      });
    } else {
      recentTable.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-light);">
            No resumes uploaded yet. Go to <a href="upload-resume.html">Upload Resumes</a> to add candidates.
          </td>
        </tr>
      `;
    }

  } catch (error) {
    console.error('Failed to load dashboard data:', error);
    Utils.showError('Could not connect to the backend server. Please verify FastAPI is running.');
  }
});
