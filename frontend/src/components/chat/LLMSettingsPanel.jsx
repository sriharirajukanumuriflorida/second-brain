import { useState } from 'react';

const LS_KEY = 'llm_config';

export function loadLLMConfig() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveLLMConfig(cfg) {
  if (cfg) localStorage.setItem(LS_KEY, JSON.stringify(cfg));
  else localStorage.removeItem(LS_KEY);
}

export default function LLMSettingsPanel({ onChange }) {
  const saved = loadLLMConfig();
  const [open, setOpen] = useState(false);
  const [provider, setProvider] = useState(saved?.provider || 'anthropic');
  const [apiKey, setApiKey] = useState(saved?.api_key || '');
  const [model, setModel] = useState(saved?.model || '');
  const [saved2, setSaved2] = useState(!!saved);

  const handleSave = () => {
    const cfg = apiKey.trim() ? { provider, api_key: apiKey.trim(), model: model.trim() || undefined } : null;
    saveLLMConfig(cfg);
    setSaved2(!!cfg);
    onChange?.(cfg);
    setOpen(false);
  };

  const handleClear = () => {
    setApiKey('');
    setModel('');
    saveLLMConfig(null);
    setSaved2(false);
    onChange?.(null);
    setOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(o => !o)}
        title="LLM settings"
        className={`p-2 rounded-md border ${saved2 ? 'border-blue-400 text-blue-600' : 'border-gray-300 text-gray-500'} hover:bg-gray-100`}
      >
        ⚙️
        {saved2 && <span className="ml-1 text-xs font-medium">Custom key</span>}
      </button>

      {open && (
        <div className="absolute right-0 bottom-12 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50">
          <h3 className="text-sm font-semibold text-gray-800 mb-3">LLM Settings</h3>
          <p className="text-xs text-gray-500 mb-3">
            Provide your own keys to use your quota. Leave blank to use the server's configured LLM.
          </p>

          <div className="space-y-3">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Provider</label>
              <select
                value={provider}
                onChange={e => setProvider(e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
              >
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="openai">OpenAI (GPT)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-600 mb-1">API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={e => setApiKey(e.target.value)}
                placeholder="sk-... or sk-ant-..."
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-600 mb-1">Model (optional)</label>
              <input
                type="text"
                value={model}
                onChange={e => setModel(e.target.value)}
                placeholder={provider === 'anthropic' ? 'claude-3-5-sonnet-20241022' : 'gpt-4o'}
                className="w-full px-2 py-1.5 border border-gray-300 rounded text-sm"
              />
            </div>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={handleSave}
              className="flex-1 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
            >
              Save
            </button>
            {saved2 && (
              <button
                onClick={handleClear}
                className="px-3 py-1.5 border border-gray-300 text-sm rounded hover:bg-gray-50"
              >
                Clear
              </button>
            )}
            <button
              onClick={() => setOpen(false)}
              className="px-3 py-1.5 border border-gray-300 text-sm rounded hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
