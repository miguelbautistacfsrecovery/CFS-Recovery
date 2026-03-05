// Thriver AI - Chat Frontend
// State
let authToken = localStorage.getItem('thriver_token');
let messagesRemaining = 50;
let sessionMessages = [];
let isStreaming = false;

// DOM Elements
const screens = {
    landing: document.getElementById('screen-landing'),
    expired: document.getElementById('screen-expired'),
    chat: document.getElementById('screen-chat'),
};
const emailInput = document.getElementById('email-input');
const signupBtn = document.getElementById('signup-btn');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const creditTracker = document.getElementById('credit-tracker');
const dailyLimitBanner = document.getElementById('daily-limit-banner');
const chatInputArea = document.getElementById('chat-input-area');

// Screen management
function showScreen(name) {
    Object.values(screens).forEach(s => s.classList.remove('active'));
    screens[name].classList.add('active');
}

// Check URL params for checkout result
function checkCheckoutResult() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('checkout') === 'success') {
        window.history.replaceState({}, '', '/');
        checkAuthStatus();
    }
}

// Initialize
async function init() {
    checkCheckoutResult();

    if (authToken) {
        await checkAuthStatus();
    } else {
        showScreen('landing');
    }
}

// Auth
async function handleSignup() {
    const email = emailInput.value.trim();
    if (!email || !email.includes('@')) {
        emailInput.style.borderColor = '#E20D0D';
        return;
    }

    signupBtn.disabled = true;
    signupBtn.textContent = 'Starting...';

    try {
        const res = await fetch(`/api/auth/signup?email=${encodeURIComponent(email)}`, {
            method: 'POST',
        });

        if (!res.ok) throw new Error('Signup failed');

        const data = await res.json();
        authToken = data.token;
        localStorage.setItem('thriver_token', authToken);
        messagesRemaining = data.messages_remaining;

        if (data.status === 'active') {
            updateCreditTracker();
            showScreen('chat');
        } else if (data.status === 'trial_expired') {
            showScreen('expired');
        }
    } catch (err) {
        console.error('Signup error:', err);
        signupBtn.textContent = 'Try again';
        signupBtn.disabled = false;
    }
}

async function checkAuthStatus() {
    try {
        const res = await fetch('/api/auth/status', {
            headers: { 'Authorization': `Bearer ${authToken}` },
        });

        if (!res.ok) {
            localStorage.removeItem('thriver_token');
            authToken = null;
            showScreen('landing');
            return;
        }

        const data = await res.json();
        messagesRemaining = data.messages_remaining;

        if (data.status === 'active') {
            updateCreditTracker();
            showScreen('chat');
            if (messagesRemaining <= 0) {
                showDailyLimit();
            }
        } else if (data.status === 'trial_expired') {
            showScreen('expired');
        } else {
            showScreen('expired');
        }
    } catch {
        showScreen('landing');
    }
}

async function handleSubscribe() {
    try {
        const res = await fetch('/api/billing/create-checkout', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${authToken}` },
        });
        const data = await res.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        }
    } catch (err) {
        console.error('Checkout error:', err);
    }
}

// Credit tracker — only visible when running low to avoid anxiety
function updateCreditTracker() {
    if (messagesRemaining <= 10) {
        creditTracker.textContent = `${messagesRemaining} left today`;
        creditTracker.style.display = '';
        if (messagesRemaining <= 5) {
            creditTracker.style.color = '#F59E0B';
        } else {
            creditTracker.style.color = '';
        }
    } else {
        creditTracker.style.display = 'none';
    }
}

function showDailyLimit() {
    dailyLimitBanner.classList.remove('hidden');
    chatInputArea.classList.add('hidden');
}

// Chat
function addMessage(role, content) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
    return contentDiv;
}

function addTypingIndicator() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant';
    msgDiv.id = 'typing-indicator';
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    msgDiv.appendChild(indicator);
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
}

function addUpsellCard(message) {
    const card = document.createElement('div');
    card.className = 'upsell-card';
    card.innerHTML = `<p>${escapeHtml(message.split('Apply here:')[0].trim())}</p><a href="https://www.cfsrecovery.co/apply" target="_blank" class="upsell-link">Apply Here</a>`;
    chatMessages.appendChild(card);
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Auto-resize textarea
chatInput.addEventListener('input', () => {
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isStreaming) return;

    if (messagesRemaining <= 0) {
        showDailyLimit();
        return;
    }

    isStreaming = true;
    sendBtn.disabled = true;
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Add user message
    addMessage('user', message);
    sessionMessages.push({ role: 'user', content: message });

    // Show typing indicator
    addTypingIndicator();

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
            },
            body: JSON.stringify({
                message: message,
                session_messages: sessionMessages.slice(-10),
            }),
        });

        if (res.status === 429) {
            removeTypingIndicator();
            showDailyLimit();
            isStreaming = false;
            sendBtn.disabled = false;
            return;
        }

        if (res.status === 403) {
            removeTypingIndicator();
            const data = await res.json();
            if (data.detail === 'trial_expired') {
                showScreen('expired');
            }
            isStreaming = false;
            sendBtn.disabled = false;
            return;
        }

        if (!res.ok) {
            removeTypingIndicator();
            addMessage('assistant', 'Something went wrong. Please try again.');
            isStreaming = false;
            sendBtn.disabled = false;
            return;
        }

        // Stream the response
        removeTypingIndicator();
        const assistantContent = addMessage('assistant', '');
        let fullText = '';

        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const jsonStr = line.slice(6);
                try {
                    const data = JSON.parse(jsonStr);

                    if (data.text) {
                        fullText += data.text;
                        assistantContent.textContent = fullText;
                        scrollToBottom();
                    }

                    if (data.upsell) {
                        addUpsellCard(data.upsell);
                    }

                    if (data.done) {
                        if (data.messages_remaining !== undefined) {
                            messagesRemaining = data.messages_remaining;
                            updateCreditTracker();
                        }
                    }

                    if (data.error) {
                        console.error('Stream error:', data.error);
                    }
                } catch {
                    // Skip malformed JSON
                }
            }
        }

        sessionMessages.push({ role: 'assistant', content: fullText });

    } catch (err) {
        removeTypingIndicator();
        addMessage('assistant', 'Connection issue. Please try again.');
        console.error('Chat error:', err);
    }

    isStreaming = false;
    sendBtn.disabled = false;
    chatInput.focus();
}

// Initialize on load
init();
