import { marked } from 'marked';
import { supabase } from '../supabaseClient';
import { auth } from '../auth';
import { i18n } from '../i18n';
import { EnhancedSearchService } from '../services/enhanced-search';

import mermaid from 'mermaid';

// --- Types ---
type Sender = 'user' | 'ai';
interface Message { id?: number; sender: Sender; content: string; }
// Add Source type for citations
interface Source {
    source: string;
    page?: number;
    user_id?: string;
    chat_id?: string;
}
interface Chat { id: string; title: string; messages: Message[]; dify_conversation_id?: string; has_document?: boolean; document_filename?: string; createdAt?: string; }
interface AppState { chats: Chat[]; activeChatId: string | null; }

interface SpeechRecognitionEvent extends Event { results: SpeechRecognitionResultList; }
interface SpeechRecognitionErrorEvent extends Event { error: string; }
declare var webkitSpeechRecognition: any;
declare var SpeechRecognition: any;
declare global {
    interface Window {
        SpeechRecognition?: typeof SpeechRecognition;
        webkitSpeechRecognition?: typeof webkitSpeechRecognition;
    }
}

export async function renderAppPage(container: HTMLElement) {
    const GUEST_STORAGE_KEY = 'legalAI.guestChats';
    const GUEST_USER_ID_KEY = 'legalAI.guestUserId';

    const enhancedSearch = new EnhancedSearchService();

    let appState: AppState;
    const session = auth.getSession();
    let isGuestMode = session === null;

    const SUGGESTED_QUERIES = ['app_query_1', 'app_query_2', 'app_query_3', 'app_query_4'];

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = SpeechRecognitionAPI ? new SpeechRecognitionAPI() : null;
    const synthesis = window.speechSynthesis;
    let isListening = false;

    function getOrCreateGuestUserId(): string {
        let guestId = localStorage.getItem(GUEST_USER_ID_KEY);
        if (!guestId) {
            guestId = `guest_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
            localStorage.setItem(GUEST_USER_ID_KEY, guestId);
        }
        return guestId;
    }
    let userIdentifier = session?.user?.id || getOrCreateGuestUserId();

    // --- HTML Structure ---
    container.innerHTML = `
      <div class="app-layout">
          <aside class="sidebar">
              <div class="sidebar-top">
                <button class="new-chat-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                    ${i18n.t('app_newChat')}
                </button>
                <div class="sidebar-role-selector">
                    <label for="role-selector">${i18n.t('app_iAmA')}</label>
                    <select id="role-selector">
                        <option value="General Public" selected>${i18n.t('app_role_general')}</option>
                        <option value="Law Student">${i18n.t('app_role_student')}</option>
                        <option value="Legal Professional">${i18n.t('app_role_professional')}</option>
                    </select>
                </div>
              </div>
              <div class="conversation-list"><h2>${i18n.t('app_history')}</h2></div>
              <div class="sidebar-footer">
                  <div id="dark-mode-toggle">
                       <svg class="icon" id="theme-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"></path></svg>
                       <span id="theme-text">${document.body.classList.contains('dark-mode') ? i18n.t('app_lightMode') : i18n.t('app_darkMode')}</span>
                  </div>
                  <div id="sidebar-lang-switcher" class="language-switcher-sidebar">
                      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                      <span class="lang-en ${i18n.getLanguage() === 'en' ? 'lang-active' : ''}">EN</span>
                      <span>/</span>
                      <span class="lang-bn ${i18n.getLanguage() === 'bn' ? 'lang-active' : ''}">বাং</span>
                  </div>
                  <div id="user-profile-link" class="user-profile-link"></div>
              </div>
          </aside>
          <main class="main-content">
               <div class="chat-header-bar">
                   <div id="role-chip" class="role-chip">
                       <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                       <span id="role-chip-label">General Public</span>
                       <svg class="role-chip-caret" xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
                   </div>
                   <div id="role-dropdown" class="role-dropdown" hidden>
                       <div class="role-option" data-role="General Public">
                           <span class="role-option-name">General Public</span>
                           <span class="role-option-desc">Plain language, practical advice</span>
                       </div>
                       <div class="role-option" data-role="Law Student">
                           <span class="role-option-name">Law Student</span>
                           <span class="role-option-desc">Case law, theory & academic context</span>
                       </div>
                       <div class="role-option" data-role="Legal Professional">
                           <span class="role-option-name">Legal Professional</span>
                           <span class="role-option-desc">Precise statutory & procedural guidance</span>
                       </div>
                   </div>
               </div>
              <div id="chat-window"></div>
              <div class="message-form-container">
                  <form id="message-form">
                      <button type="button" id="upload-doc-btn" class="upload-btn" title="Document upload feature">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
                      </button>
                      <button type="button" id="mic-button" class="mic-btn" title="Ask with voice">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line></svg>
                      </button>
                      <input type="text" id="message-input" placeholder="${i18n.t('app_askAnything')}" autocomplete="off" required>
                      <button type="submit" id="send-button">
                          <svg class="icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                      </button>
                  </form>
              </div>
          </main>
          <div id="overlay"></div>
      </div>`;

    const uploadDocBtn = document.getElementById('upload-doc-btn') as HTMLButtonElement;
    const sidebar = document.querySelector('.sidebar') as HTMLElement;
    const overlay = document.getElementById('overlay') as HTMLDivElement;
    const chatWindow = document.getElementById('chat-window') as HTMLDivElement;
    const messageForm = document.getElementById('message-form') as HTMLFormElement;
    const messageInput = document.getElementById('message-input') as HTMLInputElement;
    const newChatBtn = document.querySelector('.new-chat-btn') as HTMLButtonElement;
    const conversationList = document.querySelector('.conversation-list') as HTMLDivElement;
    const darkModeToggle = document.getElementById('dark-mode-toggle') as HTMLDivElement;
    const themeText = document.getElementById('theme-text') as HTMLSpanElement;
    const userProfileLink = document.getElementById('user-profile-link') as HTMLDivElement;
    const micButton = document.getElementById('mic-button') as HTMLButtonElement;
    const sidebarLangSwitcher = document.getElementById('sidebar-lang-switcher');

    function speakText(text: string) {
        if (synthesis.speaking) synthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = synthesis.getVoices();
        const langCode = i18n.getLanguage();
        const preferredVoice = voices.find(voice => voice.lang.startsWith(langCode) && voice.name.includes('Google'));
        utterance.voice = preferredVoice || voices.find(voice => voice.lang.startsWith(langCode)) || voices[0];
        const lastMessageAvatar = chatWindow.querySelector('.message-wrapper:last-child .ai-avatar');
        utterance.onstart = () => { lastMessageAvatar?.classList.add('is-speaking'); };
        utterance.onend = () => { lastMessageAvatar?.classList.remove('is-speaking'); };
        utterance.onerror = () => { lastMessageAvatar?.classList.remove('is-speaking'); };
        utterance.rate = 1;
        utterance.pitch = 1;
        synthesis.speak(utterance);
    }

    function getActiveChat(): Chat | undefined {
        if (!appState || !appState.activeChatId) return undefined;
        return appState.chats.find(c => c.id === appState.activeChatId);
    }

    function renderSidebar() {
        if (!conversationList) return;
        conversationList.innerHTML = ''; // removed the h2 app_history

        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const groups = {
            today: [] as Chat[],
            yesterday: [] as Chat[],
            previous: [] as Chat[]
        };

        (appState.chats || []).forEach(chat => {
            if (!chat.createdAt) {
                groups.previous.push(chat);
                return;
            }
            const chatDate = new Date(chat.createdAt);
            if (chatDate >= today) {
                groups.today.push(chat);
            } else if (chatDate >= yesterday) {
                groups.yesterday.push(chat);
            } else {
                groups.previous.push(chat);
            }
        });

        function renderGroup(title: string, chats: Chat[]) {
            if (chats.length === 0) return;

            const groupHeader = document.createElement('div');
            groupHeader.className = 'sidebar-group-label';
            groupHeader.textContent = title;
            conversationList.appendChild(groupHeader);

            chats.forEach(chat => {
                const convoItem = document.createElement('div');
                convoItem.className = 'conversation-item grouped-item';
                if (chat.id === appState.activeChatId) convoItem.classList.add('active');

                const titleArea = document.createElement('div');
                titleArea.className = 'conversation-title-area';
                titleArea.innerHTML = `<span class="bullet">•</span><span class="chat-title-text">${chat.title}</span>`;
                titleArea.addEventListener('click', () => setActiveChat(chat.id));
                convoItem.appendChild(titleArea);

                const actionsMenu = document.createElement('div');
                actionsMenu.className = 'conversation-actions';
                actionsMenu.innerHTML = `
                    <button class="action-btn rename-btn" title="Rename">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="action-btn delete-btn" title="Delete">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                `;
                actionsMenu.querySelector('.rename-btn')?.addEventListener('click', (e) => { e.stopPropagation(); renameChat(chat.id); });
                actionsMenu.querySelector('.delete-btn')?.addEventListener('click', (e) => { e.stopPropagation(); deleteChat(chat.id); });

                convoItem.appendChild(actionsMenu);
                conversationList.appendChild(convoItem);
            });
        }

        renderGroup('TODAY', groups.today);
        renderGroup('YESTERDAY', groups.yesterday);
        renderGroup('PREVIOUS', groups.previous);
    }

    function renderChatWindow() {
        if (!chatWindow) return;
        const activeChat = getActiveChat();
        const showWelcomeScreen = !activeChat || (activeChat.messages.length === 1 && activeChat.messages[0].sender === 'ai');
        if (showWelcomeScreen) {
            const suggestedQueriesHTML = SUGGESTED_QUERIES.map(key => `<div class="suggested-query-item">${i18n.t(key as any)}</div>`).join('');
            chatWindow.innerHTML = `
                <div class="empty-chat-container">
                    <div class="welcome-hero">
                        <div class="welcome-icon-ring">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.153.34c-1.325 0-2.59-.523-3.536-1.465l-2.62-2.62m5.156 0l-2.62 2.62m-5.156 0l-2.62-2.62m6.75-10.726C12 4.5 11.25 4.5 10.5 4.5c-1.01 0-2.01.143-3 .52m3-.52l-2.62 10.726" /></svg>
                        </div>
                        <p class="welcome-tagline">LEGAL INTELLIGENCE &middot; BANGLADESH</p>
                        <h2 class="welcome-heading">How may I <em>counsel you</em> today?</h2>
                        <p class="welcome-subtitle">Precise, reliable legal guidance grounded in Bangladeshi law &mdash; available at any hour.</p>
                    </div>
                    <div class="welcome-role-pills">
                        <span class="role-pill" data-role="General Public">General Public</span>
                        <span class="role-pill" data-role="Law Student">Law Student</span>
                        <span class="role-pill" data-role="Legal Professional">Legal Professional</span>
                    </div>
                    <div class="suggested-queries-container">
                        ${suggestedQueriesHTML}
                    </div>
                </div>`;
        } else {
            chatWindow.innerHTML = '';
            activeChat.messages.forEach(msg => displayMessage(msg.content, msg.sender));
        }
    }

    function displayMessage(text: string, sender: Sender, sources: Source[] = []): HTMLDivElement {
        if (!chatWindow) return document.createElement('div');

        const messageWrapper = document.createElement('div');
        messageWrapper.className = `message-wrapper ${sender}`;
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        if (sender === 'user') {
            avatar.classList.add('user-avatar');
            const user = auth.getSession()?.user;
            avatar.textContent = user?.email?.charAt(0).toUpperCase() || 'G';
        } else {
            avatar.classList.add('ai-avatar');
            avatar.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.153.34c-1.325 0-2.59-.523-3.536-1.465l-2.62-2.62m5.156 0l-2.62 2.62m-5.156 0l-2.62-2.62m6.75-10.726C12 4.5 11.25 4.5 10.5 4.5c-1.01 0-2.01.143-3 .52m3-.52l-2.62 10.726" /></svg>`;
        }
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        if (sender === 'ai') {
            const senderName = document.createElement('div');
            senderName.className = 'sender-name';
            senderName.textContent = i18n.t('app_aiSenderName');
            messageContent.appendChild(senderName);
        }
        const messageBubble = document.createElement('div');
        messageBubble.className = 'message-bubble';

        if (sender === 'ai') {
            const parsed = marked.parse(text, { gfm: true }) as string;
            messageBubble.innerHTML = parsed;
        } else {
            messageBubble.innerText = text;
        }
        messageContent.appendChild(messageBubble);

        // Add sources for AI messages
        if (sender === 'ai' && sources && sources.length > 0) {
            const sourcesContainer = document.createElement('div');
            sourcesContainer.className = 'sources-container';

            const sourcesTitle = document.createElement('h4');
            sourcesTitle.className = 'sources-title';
            sourcesTitle.textContent = 'Sources:';
            sourcesContainer.appendChild(sourcesTitle);

            const sourcesList = document.createElement('ul');
            sourcesList.className = 'sources-list';
            // Use a Set to only show unique sources
            const uniqueSources = [...new Map(sources.map(s => [`${s.source}:${s.page}`, s])).values()];

            uniqueSources.forEach(source => {
                const listItem = document.createElement('li');
                listItem.className = 'source-item';
                const pageText = source.page !== undefined ? ` - Page ${source.page + 1}` : '';
                listItem.textContent = `📄 ${source.source}${pageText}`;
                sourcesList.appendChild(listItem);
            });
            sourcesContainer.appendChild(sourcesList);
            messageContent.appendChild(sourcesContainer);
        }

        // Parse and handle follow-up questions
        let followUpQuestions: string[] = [];
        const followUpRegex = /<h4>Follow-up Suggestions:<\/h4>\s*<ol>(.*?)<\/ol>/s;
        const match = text.match(followUpRegex);

        let mainContent = text;
        if (match) {
            mainContent = text.replace(followUpRegex, '').trim();
            const listItemsRegex = /<li>(.*?)<\/li>/g;
            let itemMatch;
            while ((itemMatch = listItemsRegex.exec(match[1])) !== null) {
                followUpQuestions.push(itemMatch[1]);
            }
        }
        // --- END of new logic ---

        if (sender === 'ai') {
            const parsed = marked.parse(mainContent, { gfm: true });
            if (parsed instanceof Promise) {
                parsed.then(html => {
                    messageBubble.innerHTML = html;
                    messageBubble.querySelectorAll('.language-mermaid').forEach(async (el) => {
                        if (el instanceof HTMLElement) {
                            try {
                                const { svg } = await mermaid.render(el.id, el.textContent || '');
                                el.innerHTML = svg;
                            } catch (e) {
                                el.innerHTML = `Error rendering Mermaid diagram: ${e instanceof Error ? e.message : e}`;
                            }
                        }
                    });
                });
            } else {
                messageBubble.innerHTML = parsed;
                messageBubble.querySelectorAll('.language-mermaid').forEach(async (el) => {
                    if (el instanceof HTMLElement) {
                        const uniqueId = `mermaid-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
                        el.id = uniqueId;
                        try {
                            const { svg } = await mermaid.render(uniqueId, el.textContent || '');
                            el.innerHTML = svg;
                        } catch (e) {
                            el.innerHTML = `Error rendering Mermaid diagram: ${e instanceof Error ? e.message : e}`;
                        }
                    }
                });
            }
        } else {
            messageBubble.innerText = mainContent;
        }
        messageContent.appendChild(messageBubble);

        // --- Controls for AI messages ---
        if (sender === 'ai' && text.trim() !== "" && !text.includes('thinking')) {
            const controlsWrapper = document.createElement('div');
            controlsWrapper.className = 'message-controls';

            const feedbackControls = document.createElement('div');
            feedbackControls.className = 'feedback-controls';
            const thumbUp = document.createElement('button');
            thumbUp.className = 'feedback-btn';
            thumbUp.innerHTML = '👍';
            thumbUp.title = 'Good response';
            const thumbDown = document.createElement('button');
            thumbDown.className = 'feedback-btn';
            thumbDown.innerHTML = '👎';
            thumbDown.title = 'Bad response';

            thumbUp.addEventListener('click', () => {
                sendFeedback(getActiveChat()?.id ?? '', text, 'good');
                thumbUp.disabled = true;
                thumbDown.disabled = true;
                thumbUp.classList.add('selected');
            });

            thumbDown.addEventListener('click', () => {
                sendFeedback(getActiveChat()?.id ?? '', text, 'bad');
                thumbUp.disabled = true;
                thumbDown.disabled = true;
                thumbDown.classList.add('selected');
            });

            feedbackControls.appendChild(thumbUp);
            feedbackControls.appendChild(thumbDown);

            const speakButton = document.createElement('button');
            speakButton.className = 'speak-btn';
            speakButton.title = 'Read this message aloud';
            speakButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path></svg>`;
            speakButton.addEventListener('click', (e) => {
                e.stopPropagation();
                speakText(mainContent); // Speak only the main content
            });

            controlsWrapper.appendChild(feedbackControls);
            controlsWrapper.appendChild(speakButton);
            messageContent.appendChild(controlsWrapper);
        }

        if (sender === 'user') {
            messageWrapper.appendChild(messageContent);
            messageWrapper.appendChild(avatar);
        } else {
            messageWrapper.appendChild(avatar);
            messageWrapper.appendChild(messageContent);
        }
        chatWindow.appendChild(messageWrapper);

        // --- NEW: Render follow-up questions ---
        if (followUpQuestions.length > 0) {
            const followUpContainer = document.createElement('div');
            followUpContainer.className = 'follow-up-container';
            followUpQuestions.forEach(question => {
                const button = document.createElement('button');
                button.className = 'follow-up-question';
                button.textContent = question;
                followUpContainer.appendChild(button);
            });
            chatWindow.appendChild(followUpContainer);
        }
        // --- END of new rendering ---

        chatWindow.scrollTop = chatWindow.scrollHeight;

        return messageWrapper;
    }

    async function setActiveChat(id: string | null) {
        if (!id) { appState.activeChatId = null; renderSidebar(); renderChatWindow(); return; }
        if (appState.activeChatId === id) return;
        appState.activeChatId = id;
        const activeChat = getActiveChat();
        if (activeChat && activeChat.messages.length === 0 && !isGuestMode) {
            const { data, error } = await supabase.from('messages').select('id, content, sender').eq('chat_id', id).order('created_at', { ascending: true });
            if (error) console.error('Error fetching messages:', error);
            else if (data) activeChat.messages = data as Message[];
        }
        renderSidebar();
        renderChatWindow();
        if (window.innerWidth <= 900) { sidebar.classList.remove('is-open'); overlay.classList.remove('is-open'); }
    }

    // --- FINAL, CORRECTED loadState FUNCTION ---

    async function loadState() {
        if (isGuestMode) {
            const savedState = localStorage.getItem(GUEST_STORAGE_KEY);
            appState = savedState ? JSON.parse(savedState) : { chats: [], activeChatId: null };
            // Ensure guest chats have a createdAt since they might have been created before this feature
            appState.chats.forEach(chat => { if (!chat.createdAt) chat.createdAt = new Date().toISOString(); });
        } else {
            const { data, error } = await supabase
                .from('chats')
                .select('id, title, has_document, created_at')
                .order('created_at', { ascending: false });

            if (error) {
                console.error("Error fetching chats:", error);
                appState = { chats: [], activeChatId: null };
                return;
            }

            appState = { chats: data.map((c: any) => ({ ...c, createdAt: c.created_at, messages: [] })), activeChatId: null };
        }
    }

    async function createNewChat() {
        const initialMessage = { sender: 'ai' as Sender, content: i18n.t('app_initialGreeting') };
        if (isGuestMode) {
            const newChat: Chat = { id: `guest_${Date.now()}`, title: i18n.t('app_newChat'), messages: [initialMessage], createdAt: new Date().toISOString() };
            appState.chats.unshift(newChat);
            await setActiveChat(newChat.id);
            localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(appState));
        } else {
            const { data: { user } } = await supabase.auth.getUser();
            if (!user) return;
            const { data, error } = await supabase.from('chats').insert({ user_id: user.id, title: i18n.t('app_newChat') }).select().single();
            if (error) { console.error("Error creating chat:", error); return; }
            const newChat: Chat = { ...data, createdAt: data.created_at, messages: [initialMessage] };
            appState.chats.unshift(newChat);
            await setActiveChat(newChat.id);
        }
    }

    async function addMessageToActiveChat(message: Message, difyId?: string) {
        const activeChat = getActiveChat();
        if (!activeChat) return;
        activeChat.messages.push(message);
        if (activeChat.messages.length === 2 && message.sender === 'user') {
            const newTitle = message.content.substring(0, 30) + (message.content.length > 30 ? '...' : '');
            activeChat.title = newTitle;
            if (!isGuestMode) await supabase.from('chats').update({ title: newTitle }).eq('id', activeChat.id);
        }
        if (difyId) activeChat.dify_conversation_id = difyId;
        if (isGuestMode) {
            localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(appState));
        } else {
            const { data: { user } } = await supabase.auth.getUser();
            if (user) {
                await supabase.from('messages').insert({
                    chat_id: activeChat.id, user_id: user.id,
                    sender: message.sender, content: message.content
                });
            }
        }
        renderSidebar();
        renderChatWindow();
    }

    async function renameChat(id: string) {
        const chat = appState.chats.find(c => c.id === id);
        if (!chat) return;
        const newTitle = prompt(i18n.t('app_renameTitlePrompt'), chat.title);
        if (newTitle && newTitle.trim() !== "") {
            chat.title = newTitle.trim();
            if (isGuestMode) localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(appState));
            else await supabase.from('chats').update({ title: newTitle.trim() }).eq('id', id);
            renderSidebar();
        }
    }

    async function deleteChat(id: string) {
        if (!confirm(i18n.t('app_deleteConfirm'))) return;
        const index = appState.chats.findIndex(c => c.id === id);
        if (index > -1) {
            appState.chats.splice(index, 1);
            if (isGuestMode) localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(appState));
            else await supabase.from('chats').delete().eq('id', id);
            if (appState.activeChatId === id) {
                const nextId = appState.chats.length > 0 ? appState.chats[0].id : null;
                if (nextId) await setActiveChat(nextId);
                else await createNewChat();
            } else {
                renderSidebar();
            }
        }
    }


    async function sendFeedback(chatId: string, msgContent: string, rating: 'good' | 'bad') {
        // Save to database
        const { error } = await supabase
            .from('message_feedback')
            .insert({
                chat_id: chatId,
                message_content: msgContent,
                rating: rating
            });
        if (error) {
            console.error('Error saving feedback:', error);
        }

        // Also record in search analytics (this would need search ID in real implementation)
        // For now, we'll just log the feedback
        console.log(`📊 User feedback recorded: ${rating} for message in chat ${chatId}`);

        // Optionally get analytics insights when negative feedback is received
        if (rating === 'bad') {
            const insights = enhancedSearch.getQualityInsights();
            if (insights.suggestions.length > 0) {
                console.log(`💡 Quality suggestions:`, insights.suggestions);
            }
        }
    }


    // --- Updated handleFormSubmit with AI switching and all previous features ---

    async function handleFormSubmit() {
        const userInput = messageInput.value.trim();
        if (!userInput) return;
        if (!appState.activeChatId) await createNewChat();

        const activeChat = getActiveChat();
        if (!activeChat) return;

        await addMessageToActiveChat({ sender: 'user', content: userInput });
        messageInput.value = '';

        // Create a new, empty AI message bubble that we will stream into.
        const aiMessageWrapper = displayMessage("", 'ai');
        const aiMessageBubble = aiMessageWrapper.querySelector('.message-bubble') as HTMLDivElement;
        // Add a typing cursor for immediate feedback
        aiMessageBubble.innerHTML = '<span class="typing-cursor"></span>';

        // --- Updated handleFormSubmit with AI switching to CUSTOM BACKEND ---

        try {
            // Call the custom backend endpoint instead of Dify
            await sendQueryToCustomBackend(userInput, aiMessageWrapper);
        } catch (error) {
            aiMessageWrapper?.remove();
            const errorMessage = `${i18n.t('app_error')} ${error instanceof Error ? error.message : 'Unknown error'}`;
            await addMessageToActiveChat({ sender: 'ai', content: errorMessage });
            speakText(errorMessage);
        }
    }

    async function sendQueryToCustomBackend(query: string, tempMessageWrapper: HTMLDivElement) {
        const userRole = (document.getElementById('role-selector') as HTMLSelectElement).value;
        const requestBody = JSON.stringify({
            message: query,
            user_id: userIdentifier,
            role: userRole
        });

        console.log("Custom RAG Backend request body:", requestBody);

        // Make sure to use the deployed Render URL if testing in production later
        const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:10000';

        const response = await fetch(`${backendUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: requestBody
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorBody}`);
        }

        tempMessageWrapper.remove();

        // The FastAPI backend returns a structured JSONResponse now, not a stream (can be updated to stream later if needed)
        const data = await response.json();
        const fullResponse = data.response || "No response generated.";
        const contextUsedCount = data.context_used || 0;

        console.log(`Generated response using ${contextUsedCount} document chunks.`);

        const aiMessageWrapper = displayMessage("", 'ai');
        const aiMessageBubble = aiMessageWrapper.querySelector('.message-bubble') as HTMLDivElement;

        const parsedMarkdown = marked.parse(fullResponse, { gfm: true });
        if (parsedMarkdown instanceof Promise) {
            parsedMarkdown.then(html => { aiMessageBubble.innerHTML = html; });
        } else {
            aiMessageBubble.innerHTML = parsedMarkdown as string;
        }
        chatWindow.scrollTop = chatWindow.scrollHeight;

        return { fullResponse };
    }

    function handleDocumentUploadComingSoon() {
        alert('This feature is coming soon!');
    }

    function updateGuestModeState() {
        const currentSession = auth.getSession();
        isGuestMode = currentSession === null;
        // Update user identifier when auth state changes
        userIdentifier = currentSession?.user?.id || getOrCreateGuestUserId();
    }

    function renderGuestNotice() {
        // Remove existing guest notice
        const existingNotice = sidebar.querySelector('.guest-notice');
        if (existingNotice) {
            existingNotice.remove();
        }

        // Add guest notice if in guest mode
        if (isGuestMode) {
            const guestNotice = document.createElement('div');
            guestNotice.className = 'guest-notice';
            guestNotice.style.cssText = 'background-color: var(--bg-soft); border: 1px solid var(--border-color); color: var(--text-secondary); padding: 8px 12px; text-align: center; font-size: 14px; border-radius: 8px; margin-bottom: 16px;';
            guestNotice.innerHTML = `${i18n.t('app_guestNotice')} <a href="/login" data-link style="color: var(--accent-color-start); font-weight: 500;">${i18n.t('app_guestSignIn')}</a> ${i18n.t('app_guestToSave')}`;
            sidebar.prepend(guestNotice);
        }
    }

    function renderUserProfileLink() {
        if (!userProfileLink) return;

        if (isGuestMode) {
            userProfileLink.innerHTML = `
                <a href="/login" data-link class="footer-account-link guest-link">
                    <div class="footer-avatar guest-avatar">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path><polyline points="10 17 15 12 10 7"></polyline><line x1="15" y1="12" x2="3" y2="12"></line></svg>
                    </div>
                    <div class="footer-user-info">
                        <span class="footer-user-name">Sign In</span>
                        <span class="footer-user-plan">Log in to save chats</span>
                    </div>
                </a>
            `;
        } else {
            const currentSession = auth.getSession();
            const user = currentSession?.user;
            const name = user?.user_metadata?.full_name || user?.email?.split('@')[0] || 'User';
            const userInitial = name.charAt(0).toUpperCase();
            userProfileLink.innerHTML = `
                <a href="/profile" data-link class="footer-account-link">
                    <div class="footer-avatar">${userInitial}</div>
                    <div class="footer-user-info">
                        <span class="footer-user-name">${name}</span>
                        <span class="footer-user-plan">Pro Plan</span>
                    </div>
                    <div class="footer-more-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                    </div>
                </a>
            `;
        }
    }

    async function initApp() {
        mermaid.initialize({ startOnLoad: false });
        function setupSpeechRecognition() {
            if (!recognition) {
                if (micButton) micButton.style.display = 'none';
                console.warn("Speech Recognition not supported in this browser.");
                return;
            }
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = i18n.getLanguage() === 'bn' ? 'bn-BD' : 'en-US';
            recognition.onstart = () => { isListening = true; micButton.classList.add('is-listening'); };
            recognition.onend = () => { isListening = false; micButton.classList.remove('is-listening'); };
            recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
                console.error("Speech recognition error", event.error);
                isListening = false;
                micButton.classList.remove('is-listening');
            };
            recognition.onresult = (event: SpeechRecognitionEvent) => {
                const transcript = event.results[0][0].transcript;
                messageInput.value = transcript;
                handleFormSubmit();
            };
            micButton.addEventListener('click', () => {
                if (synthesis.speaking) { synthesis.cancel(); }
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            });
        }
        function toggleSidebar() {
            sidebar.classList.toggle('is-open');
            overlay.classList.toggle('is-open');
        }
        document.addEventListener('toggle-sidebar', toggleSidebar);
        document.addEventListener('navbar-new-chat', () => createNewChat());
        overlay.addEventListener('click', toggleSidebar);
        conversationList.addEventListener('click', (e) => {
            if (window.innerWidth <= 900 && (e.target as HTMLElement).closest('.conversation-item')) {
                toggleSidebar();
            }
        });
        messageForm.addEventListener('submit', (e) => { e.preventDefault(); handleFormSubmit(); });
        chatWindow.addEventListener('click', (e) => {
            const target = e.target as HTMLElement;
            const queryItem = target.closest('.suggested-query-item');
            const followUpItem = target.closest('.follow-up-question');

            if (queryItem && queryItem.textContent) {
                messageInput.value = queryItem.textContent;
                handleFormSubmit();
            } else if (followUpItem && followUpItem.textContent) {
                messageInput.value = followUpItem.textContent;
                handleFormSubmit();
            }
        });
        newChatBtn.addEventListener('click', createNewChat);

        // ── Role chip dropdown ──
        const roleChip = document.getElementById('role-chip') as HTMLDivElement;
        const roleDropdown = document.getElementById('role-dropdown') as HTMLDivElement;
        const roleChipLabel = document.getElementById('role-chip-label') as HTMLSpanElement;
        const roleSelectEl = document.getElementById('role-selector') as HTMLSelectElement;

        function setRole(role: string) {
            roleChipLabel.textContent = role;
            if (roleSelectEl) roleSelectEl.value = role;
            roleDropdown.hidden = true;
            roleDropdown.querySelectorAll('.role-option').forEach(opt => {
                opt.classList.toggle('active', (opt as HTMLElement).dataset.role === role);
            });
        }

        roleChip?.addEventListener('click', (e) => {
            e.stopPropagation();
            roleDropdown.hidden = !roleDropdown.hidden;
        });

        roleDropdown?.addEventListener('click', (e) => {
            const opt = (e.target as HTMLElement).closest('.role-option') as HTMLElement;
            if (opt && opt.dataset.role) setRole(opt.dataset.role);
        });

        document.addEventListener('click', () => { if (roleDropdown) roleDropdown.hidden = true; });

        // Sync welcome-screen role pills with chip
        chatWindow.addEventListener('click', (ev) => {
            const pill = (ev.target as HTMLElement).closest('.role-pill') as HTMLElement;
            if (pill && pill.dataset.role) setRole(pill.dataset.role);
        });
        darkModeToggle.addEventListener('click', () => {
            document.body.classList.toggle('dark-mode');
            if (themeText) themeText.textContent = document.body.classList.contains('dark-mode') ? i18n.t('app_lightMode') : i18n.t('app_darkMode');
        });
        renderGuestNotice();
        await loadState();
        if (appState.chats.length === 0) {
            await createNewChat();
        } else {
            await setActiveChat(appState.chats[0].id);
        }
        renderUserProfileLink();
        setupSpeechRecognition();

        // Listen for auth state changes and update UI
        window.addEventListener('authStateChange', async () => {
            updateGuestModeState();
            renderGuestNotice();
            renderUserProfileLink();
            // Reload app state when auth changes
            await loadState();
            renderSidebar();
            renderChatWindow();
        });
        sidebarLangSwitcher?.querySelector('.lang-en')?.addEventListener('click', () => {
            if (i18n.getLanguage() !== 'en') i18n.setLanguage('en');
        });
        sidebarLangSwitcher?.querySelector('.lang-bn')?.addEventListener('click', () => {
            if (i18n.getLanguage() !== 'bn') i18n.setLanguage('bn');
        });
        uploadDocBtn.addEventListener('click', handleDocumentUploadComingSoon);
    }
    await initApp();
}
