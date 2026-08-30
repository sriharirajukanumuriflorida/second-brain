import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, listChatModels } from '../api/client';
import LLMSettingsPanel, { loadLLMConfig } from '../components/chat/LLMSettingsPanel';

const SESSION_KEY = 'chat_session_id';
const HISTORY_KEY = 'chat_history';
const LLM_CONFIG_KEY = 'llm_config';
const MAX_HISTORY = 10;
const KNOWN_MODELS = {
  anthropic: [
    'claude-3-5-sonnet-20241022',
    'claude-3-5-haiku-20241022',
    'claude-3-opus-20240229',
  ],
  openai: [
    'gpt-4o',
    'gpt-4o-mini',
    'o3-mini',
  ],
};

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; }
}
function saveHistory(history) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(-MAX_HISTORY)));
}

function formatInt(value) {
  return new Intl.NumberFormat().format(value);
}

function formatUsd(value) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function buildUsageReply(messages) {
  const assistantTurns = messages.filter(
    (m) => m.role === 'assistant' && Number.isFinite(m.inputTokens) && Number.isFinite(m.outputTokens)
  );
  if (assistantTurns.length === 0) {
    return 'No usage yet. Send at least one normal message, then run /usage.';
  }

  const totals = assistantTurns.reduce(
    (acc, turn) => {
      acc.input += turn.inputTokens;
      acc.output += turn.outputTokens;
      acc.cached += turn.cached ? 1 : 0;
      acc.cost += Number.isFinite(turn.estimatedCostUsd) ? turn.estimatedCostUsd : 0;
      return acc;
    },
    { input: 0, output: 0, cached: 0, cost: 0 }
  );
  const total = totals.input + totals.output;
  const model = assistantTurns[assistantTurns.length - 1].model || 'unknown';

  return [
    `Usage (${assistantTurns.length} turns)`,
    `Input tokens: ${formatInt(totals.input)}`,
    `Output tokens: ${formatInt(totals.output)}`,
    `Total tokens: ${formatInt(total)}`,
    `Estimated cost: ${formatUsd(totals.cost)}`,
    `Cached replies: ${totals.cached}`,
    `Last model: ${model}`,
  ].join('\n');
}

async function runLocalCommand(text, messages, llmConfig, setLLMConfig) {
  const trimmed = text.trim();
  const parts = trimmed.split(/\s+/);
  const command = (parts[0] || '').toLowerCase();
  const arg = parts.slice(1).join(' ').trim();

  if (command === '/usage') return { reply: buildUsageReply(messages) };
  if (command === '/help' || command === '/commands') {
    return {
      reply: [
        'Available commands:',
        '/help - list commands',
        '/usage - token usage summary',
        '/models - show example model names',
        '/model - current LLM provider/model',
        '/model <name> - set active model',
        '/clear - clear chat history',
      ].join('\n'),
    };
  }
  if (command === '/models') {
    let liveError = null;
    if (llmConfig?.api_key) {
      try {
        const data = await listChatModels(llmConfig);
        const models = Array.isArray(data.models) ? data.models : [];
        if (models.length > 0) {
          return {
            reply: [
              `Available ${data.provider} models for your key (${models.length}):`,
              ...models.map((m) => `- ${m}`),
              '',
              'Use: /model <name>',
            ].join('\n'),
          };
        }
      } catch (err) {
        liveError = err.response?.data?.detail || 'Could not fetch live model list.';
      }
    }
    const provider = llmConfig?.provider || 'anthropic';
    const models = KNOWN_MODELS[provider] || [];
    return {
      reply: [
        ...(liveError ? [`${liveError}`, ''] : []),
        `Example ${provider} models:`,
        ...models.map((m) => `- ${m}`),
        '',
        'Add your key in ⚙️ and run /models for account-specific list.',
        'You can use any model your key supports.',
        'Use: /model <name>',
      ].join('\n'),
    };
  }
  if (command === '/model') {
    if (!arg) {
      return {
        reply: [
          'Model settings:',
          `Provider: ${llmConfig?.provider || 'server-default'}`,
          `Model: ${llmConfig?.model || 'server-default'}`,
          '',
          'Any provider-supported model name works here.',
          'Use: /model <name> to change it',
        ].join('\n'),
      };
    }
    if (!llmConfig?.api_key) {
      return { reply: 'Set your API key in ⚙️ first, then run /model <name>.' };
    }
    const next = { ...llmConfig, model: arg };
    localStorage.setItem(LLM_CONFIG_KEY, JSON.stringify(next));
    setLLMConfig(next);
    return {
      reply: [
        'Model updated.',
        `Provider: ${next.provider || 'server-default'}`,
        `Model: ${next.model}`,
      ].join('\n'),
    };
  }
  if (command === '/clear') return { clear: true };
  return { reply: `Unknown command: ${text}\nTry /help` };
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
    setError(null);
    saveHistory(newMessages);

    if (text.startsWith('/')) {
      setLoading(true);
      try {
        const commandResult = await runLocalCommand(text, newMessages, llmConfig, setLLMConfig);
        if (commandResult.clear) {
          handleNewChat();
          return;
        }
        const assistantMsg = {
          role: 'assistant',
          content: commandResult.reply,
          cached: true,
        };
        const updated = [...newMessages, assistantMsg];
        setMessages(updated);
        saveHistory(updated);
      } catch (err) {
        const detail = err.response?.data?.detail || 'Command failed. Please try again.';
        setError(detail);
      } finally {
        setLoading(false);
      }
      return;
    }

    setLoading(true);
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
        inputTokens: data.input_tokens,
        outputTokens: data.output_tokens,
        estimatedCostUsd: data.estimated_cost_usd,
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
          <p className="text-xs text-gray-500">Ask anything about your vault. I can search the web when needed.</p>
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
            placeholder="Ask your mentor… (/help for commands, Shift+Enter for new line)"
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
