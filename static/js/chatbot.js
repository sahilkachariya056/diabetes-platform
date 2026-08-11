/* chatbot.js — Full chat interface logic */

document.addEventListener('DOMContentLoaded', () => {

  const chatMessages     = document.getElementById('chatMessages');
  const chatInput        = document.getElementById('chatInput');
  const sendBtn          = document.getElementById('sendBtn');
  const typingIndicator  = document.getElementById('typingIndicator');
  const clearChat        = document.getElementById('clearChat');
  const quickTopics      = document.querySelectorAll('.qtopic');

  /* ── Auto-resize textarea ── */
  chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
  });

  /* ── Enter to send (Shift+Enter = newline) ── */
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  if (sendBtn) sendBtn.addEventListener('click', sendMessage);

  /* ── Quick topic buttons ── */
  quickTopics.forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.dataset.msg;
      if (msg) {
        chatInput.value = msg;
        sendMessage();
      }
    });
  });

  /* ── Clear chat ── */
  if (clearChat) {
    clearChat.addEventListener('click', () => {
      if (!confirm('Clear conversation history?')) return;
      // Keep only the initial welcome message
      const allMsgs = chatMessages.querySelectorAll('.chat-msg');
      allMsgs.forEach((msg, i) => { if (i > 0) msg.remove(); });
    });
  }

  /* ── Append message to chat ── */
  function appendMessage(role, text, isHTML = false) {
    const wrap = document.createElement('div');
    wrap.className = `chat-msg ${role === 'user' ? 'user-msg' : 'bot-msg'}`;

    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (role === 'user') {
      wrap.innerHTML = `
        <div class="msg-bubble">
          <p>${escapeHtml(text)}</p>
          <span class="msg-time">${time}</span>
        </div>`;
    } else {
      wrap.innerHTML = `
        <div class="msg-avatar"><i class="bi bi-heart-pulse-fill"></i></div>
        <div class="msg-bubble">
          ${isHTML ? text : `<p>${formatBotText(text)}</p>`}
          <span class="msg-time">${time}</span>
        </div>`;
    }

    chatMessages.appendChild(wrap);
    scrollToBottom();
    return wrap;
  }

  /* ── Format bot text (basic markdown-like) ── */
  function formatBotText(text) {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n•\s*/g, '<br>• ')
      .replace(/\n-\s*/g, '<br>• ')
      .replace(/\n(\d+\.)/g, '<br>$1')
      .replace(/\n/g, '<br>');
  }

  function escapeHtml(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  /* ── Scroll chat to bottom ── */
  function scrollToBottom() {
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: 'smooth' });
  }

  /* ── Show/hide typing indicator ── */
  function showTyping() {
    typingIndicator.classList.remove('hidden');
    scrollToBottom();
  }
  function hideTyping() {
    typingIndicator.classList.add('hidden');
  }

  /* ── Send message ── */
async function sendMessage() {
  const text = chatInput.value.trim();

  // Don't send empty messages
  if (!text) return;

  // Display user's message
  appendMessage('user', text);

  // Clear input
  chatInput.value = '';
  chatInput.style.height = 'auto';

  // Disable send button while waiting
  sendBtn.disabled = true;

  // Show typing animation
  showTyping();

  try {

    // Send message to Flask backend
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text
      })
    });

    // Check HTTP status
    if (!res.ok) {
      throw new Error(`Server error: ${res.status}`);
    }

    // Convert response to JSON
    const data = await res.json();

    // Hide typing animation
    hideTyping();

    // Check backend error
    if (data.error) {
      throw new Error(data.error);
    }

    // Display Gemini/rule-based response
    appendMessage('bot', data.reply);

    // Optional: useful for debugging
    console.log('Chatbot source:', data.source);

  } catch (err) {

    // Print actual error in browser console
    console.error('Chatbot error:', err);

    // Hide typing animation
    hideTyping();

    // Display friendly error to user
    appendMessage(
      'bot',
      "I'm having trouble connecting right now. Please try again in a moment! " +
      "If you have a medical emergency, please contact a healthcare professional immediately."
    );

  } finally {

    // Re-enable send button
    sendBtn.disabled = false;

    // Put cursor back in input
    chatInput.focus();
  }
}

});
