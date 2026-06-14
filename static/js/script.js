/**
 * Cyphra State Control Logic Pipeline
 * Architectural SPA Navigation, Session Bounds Management, and Real-time Component Rendering Matrix
 */

let appState = {
    authenticated: false,
    userName: "",
    activeRoute: "landing",
    widgetOpen: false,
    chatHistory: [],
    activeFileInputTarget: null
};

// Application Init Engine Hook
document.addEventListener("DOMContentLoaded", async () => {
    await checkIdentityStatus();
    initializeChatStateHistory();
    initializeDefaultStateViews();
    initializeThemeEngine();
});

// Sync server-side session token metadata states
async function checkIdentityStatus() {
    try {
        const res = await fetch('/api/auth/status');
        const data = await res.json();
        if (data.logged_in) {
            mapAuthenticatedIdentity(data.name);
        } else {
            clearAuthenticatedIdentity();
        }
    } catch (e) {
        console.error("Identity synchronizer link offline: ", e);
    }
}

// Single Page Application View Swapper Routing Matrix
function navigateTo(targetRoute) {
    if (targetRoute === 'dashboard' && !appState.authenticated) {
        openModal('loginModal');
        showToast("Authorization parameters required to access workspace.", "error");
        return;
    }
    
    appState.activeRoute = targetRoute;
    
    // Cycle active markers on Document DOM elements
    document.querySelectorAll('.page-view').forEach(view => {
        view.classList.remove('active');
    });
    const selectedView = document.getElementById(`page-${targetRoute}`);
    if (selectedView) selectedView.classList.add('active');
    
    // FIXED: Process Navbar active indicators by matching accurate element IDs instead of textContent strings
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    const activeLink = document.getElementById(`link-${targetRoute}`);
    if (activeLink) activeLink.classList.add('active');

    const activeSidebarLink = document.getElementById(`sidebar-link-${targetRoute}`);
    if (activeSidebarLink) activeSidebarLink.classList.add('active');

    // Synchronize Chat Widget placement bounds to clear dashboard collisions
    const widgetWrapper = document.getElementById('globalFloatingWidget');
    
    if (targetRoute === 'dashboard') {
        if (widgetWrapper) widgetWrapper.classList.add('hidden');
        rebindChatWindowToDashboard();
    } else {
        if (widgetWrapper) widgetWrapper.classList.remove('hidden');
        rebindChatWindowToFloatingWidget();
    }
}

function handleStartChatting() {
    if (appState.authenticated) {
        navigateTo('dashboard');
    } else {
        toggleFloatingChatWindow(true);
    }
}

// Authentication Execution Chains
async function executeLoginFlow() {
    const email = document.getElementById('loginEmail').value;
    const pass = document.getElementById('loginPassword').value;
    const errBlock = document.getElementById('loginErrorMsg');
    
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, password: pass })
        });
        const data = await res.json();
        
        if (data.success) {
            errBlock.classList.add('hidden');
            closeModal('loginModal');
            mapAuthenticatedIdentity(data.name);
            showToast(`Welcome back, ${data.name}!`, "success");
            navigateTo('dashboard');
            // Sync chat history for newly logged-in user
            initializeChatStateHistory();
        } else {
            errBlock.textContent = data.message;
            errBlock.classList.remove('hidden');
            showToast(data.message, "error");
        }
    } catch (e) {
        errBlock.textContent = "Identity server rejection code generated.";
        errBlock.classList.remove('hidden');
        showToast("Identity server connection failed.", "error");
    }
}

async function executeSignupFlow() {
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const pass = document.getElementById('signupPassword').value;
    const errBlock = document.getElementById('signupErrorMsg');
    
    try {
        const res = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: name, email: email, password: pass })
        });
        const data = await res.json();
        
        if (data.success) {
            errBlock.classList.add('hidden');
            closeModal('signupModal');
            showToast("Account successfully provisioned! Please login.", "success");
            openModal('loginModal');
        } else {
            errBlock.textContent = data.message;
            errBlock.classList.remove('hidden');
            showToast(data.message, "error");
        }
    } catch (e) {
        errBlock.textContent = "Failed registration matrix constraint validation.";
        errBlock.classList.remove('hidden');
        showToast("Signup routine interrupted by network error.", "error");
    }
}

async function handleLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        clearAuthenticatedIdentity();
        showToast("Session authentication token shredded.", "info");
        navigateTo('landing');
        // Purge user-specific history context
        initializeChatStateHistory();
    } catch (e) {
        showToast("Error processing system logout routine.", "error");
    }
}

function mapAuthenticatedIdentity(name) {
    appState.authenticated = true;
    appState.userName = name;
    
    document.getElementById('navAuthSection').classList.add('hidden');
    document.getElementById('userProfileMenu').classList.remove('hidden');
    document.querySelectorAll('.dashboard-link').forEach(el => el.classList.remove('hidden'));
    
    document.getElementById('profileAvatarName').textContent = name.charAt(0).toUpperCase();
    document.getElementById('dropdownUserTitle').textContent = name;
}

function clearAuthenticatedIdentity() {
    appState.authenticated = false;
    appState.userName = "";
    
    document.getElementById('navAuthSection').classList.remove('hidden');
    document.getElementById('userProfileMenu').classList.add('hidden');
    document.querySelectorAll('.dashboard-link').forEach(el => el.classList.add('hidden'));
    document.getElementById('profileDropdown').classList.remove('show');
}

// Floating Widget State Intercepts
function toggleFloatingChatWindow(forceOpen = false) {
    const win = document.getElementById('floatingChatWindow');
    const openIcon = document.querySelector('.launcher-open-icon');
    const closeIcon = document.querySelector('.launcher-close-icon');
    
    if (forceOpen) appState.widgetOpen = false;
    
    if (!appState.widgetOpen) {
        win.classList.remove('hidden');
        openIcon.classList.add('hidden');
        closeIcon.classList.remove('hidden');
        appState.widgetOpen = true;
        document.getElementById('widgetTextInput').focus();
    } else {
        win.classList.add('hidden');
        openIcon.classList.remove('hidden');
        closeIcon.classList.add('hidden');
        appState.widgetOpen = false;
    }
}

function closeFloatingChatWidget() {
    document.getElementById('floatingChatWindow').classList.add('hidden');
    document.querySelector('.launcher-open-icon').classList.remove('hidden');
    document.querySelector('.launcher-close-icon').classList.add('hidden');
    appState.widgetOpen = false;
}

// Re-binding structural engines between floating frame and dashboard matrix viewports
function rebindChatWindowToDashboard() {
    const winBox = document.getElementById('floatingChatWindow');
    const targetDash = document.getElementById('dashboardChatContainer');
    if (winBox && targetDash) {
        winBox.classList.remove('hidden');
        targetDash.appendChild(winBox);
        document.querySelector('.header-controls').classList.add('hidden');
    }
}

function rebindChatWindowToFloatingWidget() {
    const winBox = document.getElementById('floatingChatWindow');
    const targetFloat = document.getElementById('globalFloatingWidget');
    if (winBox && targetFloat) {
        winBox.classList.add('hidden');
        targetFloat.appendChild(winBox);
        document.querySelector('.header-controls').classList.remove('hidden');
        appState.widgetOpen = false;
    }
}

// Core Message Submission & Processing Pipeline
function handleInputKeyDown(event, targetContext) {
    if (event.key === 'Enter') {
        executeMessageSubmission(targetContext);
    }
}

async function executeMessageSubmission(context) {
    const inputEl = document.getElementById('widgetTextInput');
    const sendBtn = document.querySelector('.btn-send-execute');
    const messageText = inputEl.value.trim();
    if (!messageText || inputEl.disabled) return;
    
    // Echo text to the visual document node stream instantly and cache it
    renderMessageBubble(messageText, 'user-bubble', true);
    inputEl.value = "";
    inputEl.disabled = true;
    if (sendBtn) sendBtn.style.opacity = "0.5";
    
    // Inject streaming animation loader indicator object
    const loaderId = injectStreamingIndicator();
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });
        const data = await response.json();
        
        removeStreamingIndicator(loaderId);
        
        // Output compilation parsing sequence
        if (data.bot_response) {
            renderMessageBubble(data.bot_response.text, 'bot-bubble', true);
            
            // Evaluate custom configuration arrays
            clearInteractiveDock();
            if (data.bot_response.carousel) {
                renderRichCarousel(data.bot_response.carousel);
            }
            // Populate contextual feedback suggestion elements automatically
            renderSuggestionChips(data.suggestions || ['Features']);
        } else {
            throw new Error(data.message || "Unknown server response");
        }
    } catch (e) {
        removeStreamingIndicator(loaderId);
        console.error("Chat Pipeline Error:", e);
        
        const errorMsg = "I'm having trouble connecting to my brain right now. Please try again in a few seconds.";
        renderMessageBubble(errorMsg, 'bot-bubble', false);
        
        clearInteractiveDock();
        renderSuggestionChips(['Retry', 'Platform Features']);
        
        showToast("Connection to Cyphra Core interrupted.", "error");
    } finally {
        inputEl.disabled = false;
        if (sendBtn) sendBtn.style.opacity = "1";
        inputEl.focus();
    }
}

function renderMessageBubble(text, bubbleType, saveToHistory = false) {
    const stream = document.getElementById('widgetMessageStream');
    if (!stream) return;

    const wrapper = document.createElement('div');
    wrapper.classList.add('message-bubble', bubbleType);
    
    const content = document.createElement('div');
    content.classList.add('bubble-content');
    // Strong sanitization layer protecting execution context from XSS strings
    content.textContent = text;
    
    const timestamp = document.createElement('div');
    timestamp.classList.add('bubble-time');
    timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    wrapper.appendChild(content);
    wrapper.appendChild(timestamp);
    stream.appendChild(wrapper);
    
    // Safe fluid programmatic viewport scroll loop activation
    stream.scrollTop = stream.scrollHeight;

    // Save state context natively if flag is active
    if (saveToHistory) {
        appState.chatHistory.push({ text: text, bubbleType: bubbleType });
        localStorage.setItem('cyphra_chat_history', JSON.stringify(appState.chatHistory));
    }
}

function injectStreamingIndicator() {
    const stream = document.getElementById('widgetMessageStream');
    const loader = document.createElement('div');
    const uid = 'loader_' + Date.now();
    loader.id = uid;
    loader.classList.add('message-bubble', 'bot-bubble', 'animated-indicator-box');
    loader.innerHTML = `<div class="typing-dots"><span>.</span><span>.</span><span>.</span></div>`;
    stream.appendChild(loader);
    stream.scrollTop = stream.scrollHeight;
    return uid;
}

function removeStreamingIndicator(uid) {
    const loader = document.getElementById(uid);
    if (loader) loader.remove();
}

// ==========================================
// CLIENT PERSISTENCE STATE SERIALIZER (FIX)
// ==========================================
function initializeChatStateHistory() {
    const currentUser = appState.authenticated ? appState.userName : "guest_session";
    const cachedUser = localStorage.getItem('cyphra_active_user') || "guest_session";

    // If active identity shifts, drop volatile cache scopes instantly
    if (cachedUser !== currentUser) {
        clearActiveChatStream();
    }
    localStorage.setItem('cyphra_active_user', currentUser);

    if (currentUser === "guest_session") return;

    const localData = localStorage.getItem('cyphra_chat_history');
    const stream = document.getElementById('widgetMessageStream');
    
    if (localData && stream) {
        try {
            appState.chatHistory = JSON.parse(localData) || [];
            if (appState.chatHistory.length > 0) {
                stream.innerHTML = ''; // Wipe fallback boilerplate message
                appState.chatHistory.forEach(msg => {
                    renderMessageBubble(msg.text, msg.bubbleType, false);
                });
            }
        } catch (err) {
            console.error("Secure tracking state recovery drop generated:", err);
            appState.chatHistory = [];
        }
    } else {
        appState.chatHistory = [];
    }
}

// Interactive Sub-Component Builders (Chips & Carousels)
function renderSuggestionChips(chipsArray) {
    const dock = document.getElementById('widgetDockPanel');
    if (!dock) return;

    const chipWrapper = document.createElement('div');
    chipWrapper.classList.add('suggestion-chips-row');
    
    chipsArray.forEach(text => {
        const chip = document.createElement('button');
        chip.classList.add('suggestion-chip');
        chip.textContent = text;
        chip.onclick = () => {
            document.getElementById('widgetTextInput').value = text;
            executeMessageSubmission('widget');
            document.getElementById('widgetTextInput').focus();
        };
        chipWrapper.appendChild(chip);
    });
    dock.appendChild(chipWrapper);
}

function renderRichCarousel(cardsData) {
    const dock = document.getElementById('widgetDockPanel');
    if (!dock) return;

    const carouselContainer = document.createElement('div');
    carouselContainer.classList.add('carousel-track-container');
    
    cardsData.forEach(card => {
        const cardNode = document.createElement('div');
        cardNode.classList.add('carousel-card');
        cardNode.innerHTML = `
            <div class="card-badge-tag">${escapeHtml(card.badge)}</div>
            <h4>${escapeHtml(card.title)}</h4>
            <p>${escapeHtml(card.description)}</p>
            <div class="card-footer"></div>
        `;

        const footer = cardNode.querySelector('.card-footer');
        const btn = document.createElement('button');
        btn.className = card.title === "Starter Plan" ? "btn btn-primary btn-sm w-full" : "btn btn-secondary btn-sm w-full";
        btn.textContent = "Select";
        
        btn.onclick = () => {
            if (appState.authenticated) {
                if (card.title === "Starter Plan") {
                    showToast(`${card.title} Already Selected.`, "info");
                } else {
                    showToast(`${card.title} optimization locked.`, "info");
                }
            } else {
                if (card.title === "Starter Plan") {
                    openModal('signupModal');
                } else {
                    showToast(`${card.title} optimization locked.`, "info");
                }
            }
        };

        footer.appendChild(btn);
        carouselContainer.appendChild(cardNode);
    });
    dock.appendChild(carouselContainer);
}

function clearInteractiveDock() {
    const dock = document.getElementById('widgetDockPanel');
    if (dock) dock.innerHTML = "";
}

function clearActiveChatStream() {
    const stream = document.getElementById('widgetMessageStream');
    if (stream) {
        stream.innerHTML = `
            <div class="message-bubble bot-bubble">
                <div class="bubble-content">Hello! I'm Cyphra. Type 'features' or just start chatting. I can answer questions about our platform, pricing plans, and more.</div>
                <div class="bubble-time">System Active</div>
            </div>
        `;
    }
    appState.chatHistory = [];
    localStorage.removeItem('cyphra_chat_history');
    clearInteractiveDock();
}

// ==========================================
// ASYNCHRONOUS NOTIFICATION SYSTEM (TOASTS)
// ==========================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Map notification types to specific audio assets
    const soundMap = {
        'success': '/static/audio/success-sound.mp3',
        'error': '/static/audio/error-sound.mp3',
        'warning': '/static/audio/warning-sound.mp3',
        'info': '/static/audio/info-sound.mp3'
    };

    const audio = new Audio(soundMap[type]);
    
    // Play sound and handle browser autoplay permissions smoothly
    audio.play().catch(error => {
        console.log("Audio playback delayed until user interacts with the page.", error);
    });

    const toastElement = document.createElement('div');
    toastElement.classList.add('toast-notification', `toast-${type}`);
    
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    toastElement.appendChild(messageSpan);

    container.appendChild(toastElement);

    // Minor structural delay to capture layout translation transitions smoothly
    setTimeout(() => { toastElement.classList.add('toast-show'); }, 20);

    setTimeout(() => {
        toastElement.classList.remove('toast-show');
        toastElement.classList.add('toast-hide');
        setTimeout(() => { toastElement.remove(); }, 300);
    }, 4000);
}

// Utility DOM Interactions
function toggleProfileDropdown() {
    document.getElementById('profileDropdown').classList.toggle('show');
}

function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
}

function switchModal(openId, closeId) {
    closeModal(closeId);
    
    // Clear error messages and reset inputs for a clean state transition
    const targetModal = document.getElementById(openId);
    if (targetModal) {
        targetModal.querySelectorAll('.error-msg-block').forEach(err => err.classList.add('hidden'));
        targetModal.querySelectorAll('input').forEach(input => input.value = '');
    }

    openModal(openId);
}

function handleModalOutSideClick(event, modalId) {
    // Implementation to close modal when clicking the overlay backdrop
    if (event.target.id === modalId) {
        closeModal(modalId);
    }
}
/**
 * Mobile Navigation Menu Toggler
 */
function toggleMobileSidebar() {
    const sidebar = document.getElementById('mobilePopupSidebar');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (sidebar && backdrop) {
        sidebar.classList.toggle('active');
        backdrop.classList.toggle('active');
    }
}

function toggleFaq(triggerElement) {
    const panel = triggerElement.nextElementSibling;
    const icon = triggerElement.querySelector('.faq-icon i');
    if (panel && icon) {
        panel.classList.toggle('open');
        if (panel.classList.contains('open')) {
            icon.className = 'fa-solid fa-minus';
        } else {
            icon.className = 'fa-solid fa-plus';
        }
    }
}

function filterFaqs() {
    const query = document.getElementById('faqSearch').value.toLowerCase();
    document.querySelectorAll('.faq-item').forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? 'block' : 'none';
    });
}

function initializeDefaultStateViews() {
    renderSuggestionChips(['Features']);
    
    // Intercept clicks outside structural drop menu limits
    window.onclick = function(e) {
        if (!e.target.matches('.profile-avatar')) {
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown && dropdown.classList.contains('show')) {
                dropdown.classList.remove('show');
            }
        }
    }
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
