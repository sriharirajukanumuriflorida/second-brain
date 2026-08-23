import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../api/client';
import LLMSettingsPanel, { loadLLMConfig } from '../components/chat/LLMSettingsPanel';

const SESSION_KEY = 'chat_session_id';
const HISTORY_KEY = 'chat_history';
const MAX_HISTORY = 10;

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
}
function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-MAX_HISTORY)));
}

function SourcesPanel({ sourceNotes, webSources }) {
  const [open, setOpen] = useState(false);
  const total = sourceNotes.length + webSources.length;
  if (total === 0) return null;
  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(o => !o)}
        className="text-xs text-blue-600 hover:underline"
      >
        {open ? '▾' : '▸'} {sourceNotes.length} vault note{sourceNotes.length !== 1 ? 's' : ''}
        {webSources.length > 0 && ` · ${webSources.length} web source${webSources.length !== 1 ? 's' : ''}`}
      </button>
      {open && (
        <div className="mt-1 pl-2 border-l-2 border-gray-200 space-y-1">
          {sourceNotes.map((p, i) => (
            <p key={i} className="text-xs text-gray-500 truncate" title={p}>📄 {p}</p>
          ))}
          {webSources.map((s, i) => (
            <a key={i} href={s.url} target="_blank" rel="noopener noreferrer"
               className="block text-xs text-blue-500 hover:underline truncate" title={s.url}>
              🌐 {s.title || s.url}
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap leading-relaxed
        ${isUser
          ? 'bg-blue-600 text-white rounded-br-sm'
          : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'}`}>
        {msg.content}
        {!isUser && (msg.sourceNotes?.length > 0 || msg.webSources?.length > 0) && (
          <SourcesPanel sourceNotes={msg.sourceNotes || []} webSources={msg.webSources || []} />
        )}
        {!isUser && msg.cached && (
          <span className="block mt-1 text-xs text-gray-400">⚡ cached</span>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState(loadHistory);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [llmConfig, setLLMConfig] = useState(loadLLMConfig);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: 'user', content: text };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setLoading(true);
    setError(null);
    saveHistory(newMessages);

    try {
      const sessionId = localStorage.getItem(SESSION_KEY) || undefined;
      const history = newMessages.slice(-MAX_HISTORY).map(m => ({ role: m.role, content: m.content }));

      const data = await sendChatMessage({
        message: text,
        sessionId,
        history,
        llmConfig,
      });

      if (data.session_id && !localStorage.getItem(SESSION_KEY)) {
        localStorage.setItem(SESSION_KEY, data.session_id);
      }

      const assistantMsg = {
        role: 'assistant',
        content: data.reply,
        sourceNotes: data.source_notes || [],
        webSources: data.web_sources || [],
        model: data.model,
        cached: data.cached,
      };
      const updated = [...newMessages, assistantMsg];
      setMessages(updated);
      saveHistory(updated);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Chat failed. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(HISTORY_KEY);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between py-3 px-1 border-b border-gray-200">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Mentor Chat</h1>
          <p className="text-xs text-gray-500">Ask anything about your vault. The LLM can search the web when needed.</p>
        </div>
        <button
          onClick={handleNewChat}
          className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-3 py-1.5 rounded-md"
        >
          New chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 px-1">
        {messages.length === 0 && (
          <div className="text-center mt-16 text-gray-400">
            <p className="text-4xl mb-3">🧠</p>
            <p className="font-medium text-gray-600">Ask your mentor anything</p>
            <p className="text-sm mt-1">Your vault notes will be used as context</p>
          </div>
        )}
        {messages.map((msg, i) => <ChatBubble key={i} msg={msg} />)}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
              <span className="text-gray-400 text-sm animate-pulse">Thinking…</span>
            </div>
          </div>
        )}
        {error && (
          <div className="text-center">
            <p className="text-sm text-red-500 bg-red-50 border border-red-200 rounded-lg px-4 py-2 inline-block">{error}</p>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <form onSubmit={handleSend} className="border-t border-gray-200 py-3 px-1">
        <div className="flex gap-2 items-end">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(e); } }}
            placeholder="Ask your mentor… (Shift+Enter for new line)"
            rows={2}
            className="flex-1 resize-none px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <div className="flex flex-col gap-1">
            <LLMSettingsPanel onChange={setLLMConfig} />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm hover:bg-blue-700 disabled:bg-gray-300"
            >
              {loading ? '…' : '↑'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
