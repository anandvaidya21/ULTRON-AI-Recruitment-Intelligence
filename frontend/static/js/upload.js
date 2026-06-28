/**
 * ULTRON AI – Job Upload Form Handling & AI Preview Integration
 */

document.addEventListener('DOMContentLoaded', () => {
  Utils.loadSidebar('upload-job');

  const jdForm = document.getElementById('jd-form');
  const submitBtn = document.getElementById('jd-submit-btn');

  const previewPlaceholder = document.getElementById('preview-placeholder');
  const previewContent = document.getElementById('preview-content');

  const prevTitle = document.getElementById('prev-title');
  const prevCompany = document.getElementById('prev-company');
  const prevSummary = document.getElementById('prev-summary');
  const prevReqSkills = document.getElementById('prev-req-skills');
  const prevTechStack = document.getElementById('prev-tech-stack');
  const prevExperience = document.getElementById('prev-experience');
  const prevEducation = document.getElementById('prev-education');
  const prevDomain = document.getElementById('prev-domain');

  const sampleBtn = document.getElementById('use-default-btn');

  // 1. Submit Form
  jdForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('job-title').value;
    const company = document.getElementById('job-company').value;
    const raw_description = document.getElementById('job-desc').value;

    submitBtn.disabled = true;
    submitBtn.textContent = 'AI is understanding job context...';

    // Show loading skeleton inside preview panel
    previewPlaceholder.style.display = 'none';
    previewContent.style.display = 'none';
    
    const skeletonId = 'preview-loading-skeleton';
    let skeletonHtml = `
      <div id="${skeletonId}" style="width: 100%; display: flex; flex-direction: column; gap: 1rem;">
        <div class="skeleton skeleton-title" style="width: 60%;"></div>
        <div class="skeleton skeleton-text" style="width: 90%;"></div>
        <div class="skeleton skeleton-text" style="width: 80%;"></div>
        <div class="skeleton skeleton-text" style="width: 75%;"></div>
        <div class="skeleton skeleton-title" style="width: 40%; margin-top: 1rem;"></div>
        <div class="skeleton skeleton-text" style="width: 90%;"></div>
      </div>
    `;
    const previewCard = document.getElementById('analysis-preview');
    previewCard.insertAdjacentHTML('beforeend', skeletonHtml);

    try {
      const data = await APIClient.post('/jobs/upload', {
        title,
        company,
        raw_description
      });

      // Remove skeleton
      document.getElementById(skeletonId)?.remove();

      // Cache active job
      Auth.setActiveJob(data.id);

      // Populate preview details
      const parsed = data.parsed_data || {};
      prevTitle.textContent = parsed.title || data.title;
      prevCompany.textContent = parsed.company || data.company || '';
      prevSummary.textContent = parsed.role_summary || 'Analyzed successfully.';
      
      prevReqSkills.innerHTML = '';
      if (parsed.required_skills && parsed.required_skills.length > 0) {
        parsed.required_skills.forEach(skill => {
          prevReqSkills.insertAdjacentHTML('beforeend', `<span class="badge badge-primary">${skill}</span>`);
        });
      } else {
        prevReqSkills.textContent = 'None extracted';
      }

      prevTechStack.innerHTML = '';
      if (parsed.tech_stack && parsed.tech_stack.length > 0) {
        parsed.tech_stack.forEach(tech => {
          prevTechStack.insertAdjacentHTML('beforeend', `<span class="badge badge-info">${tech}</span>`);
        });
      } else {
        prevTechStack.textContent = 'None extracted';
      }

      prevExperience.textContent = parsed.experience_years || 'Not specified';
      prevEducation.textContent = parsed.education || 'Not specified';
      prevDomain.textContent = `${parsed.domain || 'Software Engineering'} | ${parsed.industry || 'Technology'}`;

      // Show content
      previewContent.style.display = 'block';

    } catch (error) {
      document.getElementById(skeletonId)?.remove();
      previewPlaceholder.style.display = 'flex';
      console.error(error);
      Utils.showError(error.message || 'Failed to analyze job description.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Analyze JD via Cognitive AI';
    }
  });

  // Load sample JD helper
  sampleBtn?.addEventListener('click', () => {
    document.getElementById('job-title').value = "Full Stack Engineer (Python & React)";
    document.getElementById('job-company').value = "Redrob AI";
    document.getElementById('job-desc').value = `
Job Summary:
We are looking for a Full Stack Engineer to build core modules of our recruitment intelligence workspace. You will own backend architecture, AI system API integration, and frontend components.

Requirements:
- Minimum 3+ years experience as a software engineer.
- Hands-on expertise with Python and FastAPI/Flask backend frameworks.
- Frontend development experience with modern Javascript, HTML5, CSS3, and React.
- Understanding of databases (SQLite/PostgreSQL) and REST APIs.
- Experience with Docker containers and deployment to AWS is preferred.
- Educational Background: Bachelor's degree in Computer Science, engineering or related domain.
    `.trim();
  });
});
