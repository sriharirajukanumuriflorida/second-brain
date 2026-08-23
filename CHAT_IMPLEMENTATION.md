# Chat Interface Implementation Log

> **Feature:** LLM Mentor Chat with vault RAG + native web search + token cost controls  
> **Branch:** `main`

---

## Progress Tracker

| # | Todo ID | Description | Status |
|---|---------|-------------|--------|
| 1 | `chat-history` | Add ChatSession, ChatMessage, ChatCache DB models | ✅ Done |
| 2 | `chat-schema` | Add ChatRequest / ChatResponse Pydantic schemas | ✅ Done |
| 3 | `mentor-prompt` | Write vault-first mentor system prompt | ✅ Done |
| 4 | `cost-skills` | Build TokenBudgetService (context trim, history summarize, model routing, cache) | ✅ Done |
| 5 | `claude-web-search` | Extend ClaudeProvider with native web_search tool | ✅ Done |
| 6 | `openai-web-search` | Extend OpenAIProvider with native web_search_preview tool | ✅ Done |
| 7 | `chat-workflow` | Build MentorChatWorkflow | ✅ Done |
| 8 | `chat-api` | Create POST /api/v1/chat endpoint | ✅ Done |
| 9 | `chat-client` | Add sendChatMessage() to frontend API client | ✅ Done |
| 10 | `chat-settings-ui` | Build LLMSettingsPanel component | ✅ Done |
| 11 | `chat-ui` | Build ChatPage.jsx | ✅ Done |
| 12 | `chat-route` | Wire /chat route in App.jsx, Sidebar, vercel.json, main.py | ✅ Done |

---

## Files Created / Modified

### Backend
| File | Change |
|------|--------|
| `backend/app/models.py` | Added `ChatSession`, `ChatMessage`, `ChatCache` models |
| `backend/app/schemas.py` | Added `LLMConfig`, `ChatRequest`, `ChatResponse`, `ChatHistoryMessage`, `WebSource` |
| `backend/app/services/prompts/mentor_chat.py` | New — mentor system prompt + user template |
| `backend/app/services/token_budget.py` | New — TokenBudgetService (in progress) |
| `backend/app/services/llm/claude_provider.py` | Extended with web_search tool support (in progress) |
| `backend/app/services/llm/openai_provider.py` | Extended with web_search_preview tool (in progress) |
| `backend/app/services/workflows/mentor_chat_workflow.py` | New — MentorChatWorkflow (pending) |
| `backend/app/api/chat.py` | New — POST /api/v1/chat endpoint (pending) |
| `backend/app/main.py` | Register chat router (pending) |

### Frontend
| File | Change |
|------|--------|
| `frontend/src/api/client.js` | Add sendChatMessage() (pending) |
| `frontend/src/components/chat/LLMSettingsPanel.jsx` | New component (pending) |
| `frontend/src/pages/ChatPage.jsx` | New page (pending) |
| `frontend/src/App.jsx` | Add /chat route (pending) |
| `frontend/src/components/layout/Sidebar.jsx` | Add Chat nav item (pending) |
| `frontend/vercel.json` | Add /chat rewrite (pending) |

---

## Architecture Notes

```
User message
  → ChatPage.jsx (reads LLM config from localStorage)
  → POST /api/v1/chat { message, session_id, history, llm_config? }
  → MentorChatWorkflow
      1. TokenBudgetService.select_context()  → top-K vault notes (score ≥ 0.7, max 2000 tokens)
      2. TokenBudgetService.summarize_history() → compress old turns via cheap model
      3. TokenBudgetService.route_model()       → cheap vs powerful model
      4. TokenBudgetService.get_or_set_cache()  → 1h DB cache check
      5. Build messages: system (mentor prompt + vault context) + history + user message
      6. LLM.generate(messages, tools=[web_search])
      7. Extract reply + web_sources from tool_use blocks
  → ChatResponse { reply, session_id, source_notes, web_sources, tokens_used }
  → ChatPage renders bubbles + collapsible sources panel
```

## Cost Minimization Skills

| Skill | Strategy |
|-------|----------|
| Context trim | Only notes with score ≥ 0.7, max 5 notes, max 2000 tokens |
| History compression | Keep last 4 turns verbatim; older turns summarized by haiku/gpt-4o-mini |
| Model routing | Simple queries → claude-haiku / gpt-4o-mini; complex → sonnet / gpt-4o |
| Reply cache | 1h DB cache keyed on SHA256(query + top-3 note IDs) |

## Key Decisions

- **User API keys**: entered in UI, stored only in `localStorage`, sent per-request as `llm_config`
- **Web search**: LLM's native tools (Claude `web_search_20250305`, OpenAI `web_search_preview`) — LLM decides when to call
- **History**: last 10 messages in localStorage; older turns summarized server-side
- **Auth**: `require_read_access` — works for both GitHub login and shared-link visitors
