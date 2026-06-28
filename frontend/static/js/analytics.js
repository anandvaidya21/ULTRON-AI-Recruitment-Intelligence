/**
 * ULTRON AI – Analytics Visualization Controller
 * Integrates Chart.js for data visualization.
 */

document.addEventListener('DOMContentLoaded', async () => {
  Utils.loadSidebar('analytics');

  const githubRatio = document.getElementById('github-percentage');
  const devopsRatio = document.getElementById('devops-percentage');

  try {
    const data = await APIClient.get('/analytics');

    // Set highlights
    githubRatio.textContent = `${data.insights.github_ratio}%`;
    devopsRatio.textContent = `${data.insights.deployment_ratio}%`;

    // Global chart fonts and colors configurations matching theme
    Chart.defaults.font.family = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
    Chart.defaults.color = '#2E2A27';

    // 1. Skills Horizontal Bar Chart
    const skillsCtx = document.getElementById('skillsChart').getContext('2d');
    const skillLabels = Object.keys(data.skills_distribution || {});
    const skillValues = Object.values(data.skills_distribution || {});
    new Chart(skillsCtx, {
      type: 'bar',
      data: {
        labels: skillLabels,
        datasets: [{
          label: 'Candidates Count',
          data: skillValues,
          backgroundColor: '#A67C52',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: false } }
        }
      }
    });

    // 2. Score Histogram Vertical Bar Chart
    const scoresCtx = document.getElementById('scoresChart').getContext('2d');
    const scoreLabels = Object.keys(data.score_distribution || {});
    const scoreValues = Object.values(data.score_distribution || {});
    new Chart(scoresCtx, {
      type: 'bar',
      data: {
        labels: scoreLabels,
        datasets: [{
          label: 'Number of Candidates',
          data: scoreValues,
          backgroundColor: '#6F4E37',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: false } }
        }
      }
    });

    // 3. Experience Levels Doughnut Chart
    const expCtx = document.getElementById('experienceChart').getContext('2d');
    const expLabels = Object.keys(data.experience_distribution || {});
    const expValues = Object.values(data.experience_distribution || {});
    new Chart(expCtx, {
      type: 'doughnut',
      data: {
        labels: expLabels,
        datasets: [{
          data: expValues,
          backgroundColor: ['#DCC7AA', '#A67C52', '#6F4E37', '#2E2A27', '#E6DFD5'],
          borderWidth: 2,
          borderColor: '#FFFDF9'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right' }
        }
      }
    });

    // 4. Education Levels Doughnut Chart
    const eduCtx = document.getElementById('educationChart').getContext('2d');
    const eduLabels = Object.keys(data.education_distribution || {});
    const eduValues = Object.values(data.education_distribution || {});
    new Chart(eduCtx, {
      type: 'doughnut',
      data: {
        labels: eduLabels.length > 0 ? eduLabels : ['Bachelor\'s Degree'],
        datasets: [{
          data: eduValues.length > 0 ? eduValues : [1],
          backgroundColor: ['#6F4E37', '#A67C52', '#DCC7AA', '#E6DFD5'],
          borderWidth: 2,
          borderColor: '#FFFDF9'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right' }
        }
      }
    });

  } catch (err) {
    console.error('Failed to load analytics charts:', err);
  }
});
