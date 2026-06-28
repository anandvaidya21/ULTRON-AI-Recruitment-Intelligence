/**
 * ULTRON AI – Rankings Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  Utils.loadSidebar('rankings');

  const activeTitle = document.getElementById('active-job-title');
  const jobSelector = document.getElementById('job-selector');
  const tableBody = document.getElementById('rankings-table-body');
  const reAnalyzeBtn = document.getElementById('re-analyze-btn');
  const headline = document.getElementById('rankings-headline');

  let activeJobId = Auth.getActiveJob();

  // 1. Fetch available jobs for selector
  async function loadJobs() {
    try {
      const data = await APIClient.get('/jobs');
      jobSelector.innerHTML = '';
      if (data.jobs && data.jobs.length > 0) {
        data.jobs.forEach(job => {
          const selected = job.id == activeJobId ? 'selected' : '';
          jobSelector.insertAdjacentHTML('beforeend', `
            <option value="${job.id}" ${selected}>${job.title}</option>
          `);
        });

        if (!activeJobId) {
          activeJobId = data.jobs[0].id;
          Auth.setActiveJob(activeJobId);
        }
        loadRankings(activeJobId);
      } else {
        activeTitle.textContent = 'No Jobs Uploaded';
        tableBody.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; padding: 3rem; color: var(--text-light);">
              No active jobs found. Please go to <a href="upload-job.html">Upload Job</a> to start.
            </td>
          </tr>
        `;
      }
    } catch (err) {
      console.error(err);
    }
  }

  // 2. Fetch rankings for selected job
  async function loadRankings(jobId) {
    if (!jobId) return;

    tableBody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-light);">
          Retrieving semantic rankings...
        </td>
      </tr>
    `;

    try {
      const data = await APIClient.get(`/rankings/${jobId}`);
      activeTitle.textContent = data.job_title;
      headline.textContent = `Evaluating ${data.total_candidates} candidates matching your requirements.`;

      tableBody.innerHTML = '';
      if (data.rankings && data.rankings.length > 0) {
        data.rankings.forEach(ranked => {
          const bd = ranked.score_breakdown || {};
          const overallClass = Utils.getScoreClass(ranked.overall_score);
          const expClass = Utils.getScoreClass(bd.experience || 0);
          const skillClass = Utils.getScoreClass(bd.skills || 0);
          const projClass = Utils.getScoreClass(bd.projects || 0);

          const decision = ranked.explainability?.hiring_recommendation || 'No decision';
          const badgeClass = decision.includes('STRONG HIRE') ? 'badge-success' : 
                             decision.includes('HIRE') ? 'badge-info' : 'badge-warning';

          tableBody.insertAdjacentHTML('beforeend', `
            <tr class="fade-in-up">
              <td><strong>#${ranked.rank}</strong></td>
              <td>
                <a href="candidate-detail.html?id=${ranked.candidate_id}&job_id=${jobId}" style="font-weight: bold; color: var(--text-dark); text-decoration: none;">${ranked.candidate_name}</a>
                <div style="font-size: 0.75rem; color: var(--text-light);">${ranked.candidate_email || ''}</div>
              </td>
              <td><span style="font-weight: 600;" class="text-${skillClass}">${bd.skills ? bd.skills.toFixed(0) : 0}%</span></td>
              <td><span style="font-weight: 600;" class="text-${expClass}">${bd.experience ? bd.experience.toFixed(0) : 0}%</span></td>
              <td><span style="font-weight: 600;" class="text-${projClass}">${bd.projects ? bd.projects.toFixed(0) : 0}%</span></td>
              <td><div class="score-badge ${overallClass}" style="width: 36px; height: 36px; font-size: 0.8rem;">${ranked.overall_score.toFixed(0)}</div></td>
              <td><span class="badge ${badgeClass}" style="font-size: 0.75rem;">${decision.split(' – ').pop() || decision}</span></td>
              <td style="text-align: center;">
                <a href="candidate-detail.html?id=${ranked.candidate_id}&job_id=${jobId}" class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.75rem;">Explain Fit</a>
              </td>
            </tr>
          `);
        });
      } else {
        tableBody.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; padding: 3rem; color: var(--text-light);">
              No evaluations found for this job yet. Click "Re-run Analysis" to evaluate candidates pool.
            </td>
          </tr>
        `;
      }
    } catch (err) {
      console.error(err);
      tableBody.innerHTML = `
        <tr>
          <td colspan="8" style="text-align: center; padding: 2rem; color: var(--text-light);">
            Failed to load rankings. Please run evaluations first.
          </td>
        </tr>
      `;
    }
  }

  // 3. Selection change event
  jobSelector.addEventListener('change', (e) => {
    activeJobId = e.target.value;
    Auth.setActiveJob(activeJobId);
    loadRankings(activeJobId);
  });

  // 4. Re-analyze button trigger
  reAnalyzeBtn.addEventListener('click', async () => {
    if (!activeJobId) {
      alert('Please upload or select a job description first.');
      return;
    }

    reAnalyzeBtn.disabled = true;
    reAnalyzeBtn.textContent = 'Analyzing...';

    try {
      await APIClient.post('/analyze', { job_id: parseInt(activeJobId) });
      loadRankings(activeJobId);
    } catch (err) {
      alert(err.message || 'Analysis failed.');
    } finally {
      reAnalyzeBtn.disabled = false;
      reAnalyzeBtn.textContent = '🔄 Re-run Analysis';
    }
  });

  // Initialize
  loadJobs();
});
