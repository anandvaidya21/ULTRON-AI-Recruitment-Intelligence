/**
 * ULTRON AI – Conversational Recruiter Chat Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
  Utils.loadSidebar('chat');

  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const messagesBox = document.getElementById('chat-messages-box');
  const sendBtn = document.getElementById('send-btn');
  const contextJob = document.getElementById('context-job-title');
  const mentionedContainer = document.getElementById('mentioned-candidates-list');
  const suggestionsBox = document.getElementById('suggestions-container');

  const sessionId = localStorage.getItem('ultron_chat_session_id') || 
                    (() => {
                      const id = Math.random().toString(36).substring(2, 15);
                      localStorage.setItem('ultron_chat_session_id', id);
                      return id;
                    })();

  const jobId = Auth.getActiveJob();

  // Load Job info for contextual indicators
  if (jobId) {
    try {
      const job = await APIClient.get(`/jobs/${jobId}`);
      contextJob.textContent = job.title;
    } catch {
      contextJob.textContent = 'General Pool evaluation';
    }
  }

  // 1. Submit Query Handler
  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    await submitQuery(query);
  });

  window.submitQuery = async function(query) {
    chatInput.value = '';
    
    // Add user bubble
    appendBubble(query, 'user');
    
    // Scroll
    scrollToBottom();

    // Disable input
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Add thinking indicator
    const thinkingId = 'thinking-indicator';
    messagesBox.insertAdjacentHTML('beforeend', `
      <div class="chat-bubble assistant skeleton" id="${thinkingId}" style="width: 100px; height: 36px; padding: 0.5rem 1rem;">
        Thinking...
      </div>
    `);
    scrollToBottom();

    try {
      const reply = await APIClient.post('/chat', {
        message: query,
        session_id: sessionId,
        job_id: jobId ? parseInt(jobId) : null
      });

      // Remove thinking
      document.getElementById(thinkingId)?.remove();

      // Format markdown response (simple bolding/bullets conversion)
      const formattedResponse = formatMarkdown(reply.response);

      // Add reply bubble
      appendBubble(formattedResponse, 'assistant');

      // Update mentioned candidates context
      updateMentionedCandidates(reply.candidates_mentioned);

      // Update suggestions chips
      updateSuggestions(reply.suggestions);

    } catch (err) {
      document.getElementById(thinkingId)?.remove();
      appendBubble(`Failed to connect to assistant: ${err.message}`, 'assistant');
    } finally {
      chatInput.disabled = false;
      sendBtn.disabled = false;
      chatInput.focus();
      scrollToBottom();
    }
  };

  function appendBubble(content, role) {
    messagesBox.insertAdjacentHTML('beforeend', `
      <div class="chat-bubble ${role} fade-in-up">
        ${content}
      </div>
    `);
  }

  function scrollToBottom() {
    messagesBox.scrollTop = messagesBox.scrollHeight;
  }

  // Helper to highlight candidate names in sidebar context
  async function updateMentionedCandidates(candidateIds) {
    if (!candidateIds || candidateIds.length === 0) return;
    
    mentionedContainer.innerHTML = '';
    
    for (let id of candidateIds) {
      try {
        const cand = await APIClient.get(`/candidates/${id}`);
        mentionedContainer.insertAdjacentHTML('beforeend', `
          <div style="background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: 0.5rem 0.75rem; display: flex; justify-content: space-between; align-items: center;" class="fade-in-up">
            <span style="font-weight: 600; font-size: 0.85rem;">${cand.name}</span>
            <a href="candidate-detail.html?id=${cand.id}" class="btn btn-primary" style="padding: 0.2rem 0.5rem; font-size: 0.7rem; border-radius: 4px;">Profile</a>
          </div>
        `);
      } catch (err) {
        console.warn(err);
      }
    }
  }

  function updateSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return;
    suggestionsBox.innerHTML = '';
    suggestions.forEach(s => {
      // Shorten chips
      const label = s.length > 25 ? s.substring(0, 25) + '...' : s;
      suggestionsBox.insertAdjacentHTML('beforeend', `
        <span class="suggestion-chip" onclick="submitQuery('${s.replace(/'/g, "\\'")}')">${label}</span>
      `);
    });
  }

  function formatMarkdown(text) {
    // Basic formatting converter
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');
    return formatted;
  }
});
