import type { ResearchResult, Role } from './services';

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  result?: ResearchResult;
  timestamp: string;
  error?: string;
}

export interface ChatThread {
  id: string;
  role: Role;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

const STORAGE_KEY = 'justor_chat_threads_v3';
const ACTIVE_PREFIX = 'justor_active_thread_';

export const chatStore = {
  getAllThreads(): ChatThread[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as ChatThread[]) : [];
    } catch {
      return [];
    }
  },

  getThreadsByRole(role: Role): ChatThread[] {
    return this.getAllThreads()
      .filter((t) => t.role === role)
      .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
  },

  getThread(id: string): ChatThread | undefined {
    return this.getAllThreads().find((t) => t.id === id);
  },

  getActiveThreadId(role: Role): string | null {
    return localStorage.getItem(`${ACTIVE_PREFIX}${role}`);
  },

  setActiveThreadId(role: Role, id: string | null): void {
    if (id) {
      localStorage.setItem(`${ACTIVE_PREFIX}${role}`, id);
    } else {
      localStorage.removeItem(`${ACTIVE_PREFIX}${role}`);
    }
  },

  getOrCreateActiveThread(role: Role): ChatThread {
    const activeId = this.getActiveThreadId(role);
    if (activeId) {
      const found = this.getThread(activeId);
      if (found && found.role === role) return found;
    }
    const existing = this.getThreadsByRole(role);
    if (existing.length > 0) {
      this.setActiveThreadId(role, existing[0].id);
      return existing[0];
    }
    return this.createThread(role);
  },

  createThread(role: Role, initialTitle?: string): ChatThread {
    const newThread: ChatThread = {
      id: `th_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      role,
      title: initialTitle || (role === 'professional' ? 'New Legal Research' : role === 'student' ? 'New Study Session' : 'New Legal Inquiry'),
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    const all = this.getAllThreads();
    all.unshift(newThread);
    this.saveAllThreads(all);
    this.setActiveThreadId(role, newThread.id);
    return newThread;
  },

  addMessage(threadId: string, message: Omit<ChatMessage, 'id' | 'timestamp'>): ChatThread | undefined {
    const all = this.getAllThreads();
    const thread = all.find((t) => t.id === threadId);
    if (!thread) return undefined;

    const fullMsg: ChatMessage = {
      id: `msg_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
      timestamp: new Date().toISOString(),
      ...message,
    };

    thread.messages.push(fullMsg);
    thread.updatedAt = new Date().toISOString();

    // Auto update thread title from first user query if still generic
    if (thread.messages.length === 1 && message.sender === 'user') {
      const clean = message.content.trim().replace(/^(\s*["'])+|(["']\s*)+$/g, '');
      thread.title = clean.length > 40 ? `${clean.slice(0, 37)}...` : clean;
    }

    this.saveAllThreads(all);
    return thread;
  },

  deleteThread(threadId: string, role: Role): void {
    let all = this.getAllThreads();
    all = all.filter((t) => t.id !== threadId);
    this.saveAllThreads(all);

    const activeId = this.getActiveThreadId(role);
    if (activeId === threadId) {
      const remaining = all.filter((t) => t.role === role);
      this.setActiveThreadId(role, remaining.length > 0 ? remaining[0].id : null);
    }
  },

  clearAllForRole(role: Role): void {
    let all = this.getAllThreads();
    all = all.filter((t) => t.role !== role);
    this.saveAllThreads(all);
    this.setActiveThreadId(role, null);
  },

  saveAllThreads(threads: ChatThread[]): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(threads));
    } catch (e) {
      console.error('Error persisting Justor chat threads:', e);
    }
  },
};
