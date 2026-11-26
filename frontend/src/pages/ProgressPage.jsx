import { useState, useEffect } from 'react';
import {
  getProgressSummary,
  setTopicStatus,
  getQuizQuestion,
  submitQuizAnswer,
} from '../api/client';

function ScoreBadge({ score }) {
  if (score == null) return <span className="text-xs text-gray-400">no attempts</span>;
  const color = score >= 90 ? 'text-green-600' : score >= 70 ? 'text-amber-600' : 'text-red-600';
  return <span className={`text-xs font-semibold ${color}`}>{score}/100</span>;
}

function QuizPanel({ notePath, label, onClose, onScored }) {
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getQuizQuestion(notePath)
      .then((data) => setQuestion(data.question))
      .catch((err) => setError(err.response?.data?.detail || 'Could not load a question for this topic.'))
      .finally(() => setLoading(false));
  }, [notePath]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!answer.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const data = await submitQuizAnswer(notePath, question, answer);
      setResult(data);
      onScored?.();
    } catch (err) {
      setError(err.response?.data?.detail || 'Scoring failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mt-3 p-4 bg-gray-50 border border-gray-200 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold text-gray-900">Drill: {label}</h3>
        <button onClick={onClose} className="text-xs text-gray-400 hover:text-gray-600">✕</button>
      </div>

      {loading && <p className="text-sm text-gray-500">Loading a question…</p>}
      {error && <p className="text-sm text-red-500">{error}</p>}

      {question && !result && (
        <form onSubmit={handleSubmit} className="space-y-2">
          <p className="text-sm text-gray-800 font-medium">{question}</p>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={4}
            placeholder="Type your answer…"
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <button
            type="submit"
            disabled={submitting || !answer.trim()}
            className="px-4 py-1.5 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700 disabled:bg-gray-300"
          >
            {submitting ? 'Scoring…' : 'Submit answer'}
          </button>
        </form>
      )}

      {result && (
        <div className="space-y-2">
          <p className="text-sm font-semibold">
            Score: <ScoreBadge score={result.score} />
          </p>
          <p className="text-sm text-gray-700">{result.feedback}</p>
          {result.reinforcement && (
            <p className="text-sm text-gray-700 bg-blue-50 border border-blue-100 rounded-md p-2">
              <span className="font-medium">Mental model worth remembering: </span>
              {result.reinforcement}
            </p>
          )}
          <button
            onClick={onClose}
            className="text-xs text-blue-600 hover:underline"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}

function TopicRow({ topic, onMarkDone, onDrill }) {
  return (
    <div className="flex items-center justify-between py-2 px-3 hover:bg-gray-50 rounded-md">
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={topic.status === 'done'}
          onChange={() => onMarkDone(topic.note_path, topic.status === 'done' ? 'not_started' : 'done')}
          className="w-4 h-4"
        />
        <span className={`text-sm ${topic.status === 'done' ? 'text-gray-500 line-through' : 'text-gray-800'}`}>
          {topic.label}
        </span>
      </div>
      <div className="flex items-center gap-3">
        <ScoreBadge score={topic.average_score != null ? Math.round(topic.average_score) : null} />
        <button
          onClick={() => onDrill(topic.note_path, topic.label)}
          className="text-xs text-blue-600 hover:underline"
        >
          Drill me
        </button>
      </div>
    </div>
  );
}

function PhaseSection({ phase, onMarkDone, onDrill }) {
  const [open, setOpen] = useState(false);
  const pct = phase.total_topics > 0 ? Math.round((phase.done_topics / phase.total_topics) * 100) : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-3">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between p-4 text-left"
      >
        <div>
          <h3 className="font-semibold text-gray-900">{phase.phase}</h3>
          <p className="text-xs text-gray-500">{phase.done_topics} / {phase.total_topics} done</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div className="h-full bg-blue-600" style={{ width: `${pct}%` }} />
          </div>
          <span className="text-sm text-gray-600">{pct}%</span>
          <span className="text-gray-400">{open ? '▾' : '▸'}</span>
        </div>
      </button>
      {open && (
        <div className="border-t border-gray-100 p-2">
          {phase.topics.map((t) => (
            <TopicRow key={t.note_path} topic={t} onMarkDone={onMarkDone} onDrill={onDrill} />
          ))}
        </div>
      )}
    </div>
  );
}

function ProgressPage() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [drilling, setDrilling] = useState(null); // { notePath, label }

  const load = () => {
    getProgressSummary()
      .then(setSummary)
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load progress.'))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleMarkDone = async (notePath, status) => {
    await setTopicStatus(notePath, status);
    load();
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Progress</h1>
        <p className="text-gray-500">Loading…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Progress</h1>
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  const overallPct = summary.total_topics > 0
    ? Math.round((summary.done_topics / summary.total_topics) * 100)
    : 0;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Progress</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Overall</h2>
        <p className="text-4xl font-bold text-blue-600">{overallPct}%</p>
        <p className="text-sm text-gray-500 mt-1">{summary.done_topics} / {summary.total_topics} topics done</p>
      </div>

      {summary.weak_topics.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-amber-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Weak topics — review these first</h2>
          <div className="space-y-1">
            {summary.weak_topics.map((t) => (
              <div key={t.note_path} className="flex items-center justify-between">
                <span className="text-sm text-gray-800">{t.label}</span>
                <div className="flex items-center gap-3">
                  <ScoreBadge score={t.average_score != null ? Math.round(t.average_score) : null} />
                  <button
                    onClick={() => setDrilling({ notePath: t.note_path, label: t.label })}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Drill me
                  </button>
                </div>
              </div>
            ))}
          </div>
          {drilling && (
            <QuizPanel
              notePath={drilling.notePath}
              label={drilling.label}
              onClose={() => setDrilling(null)}
              onScored={load}
            />
          )}
        </div>
      )}

      <h2 className="text-lg font-semibold text-gray-900 mb-3">By phase</h2>
      {summary.phases.map((phase) => (
        <PhaseSection
          key={phase.phase}
          phase={phase}
          onMarkDone={handleMarkDone}
          onDrill={(notePath, label) => setDrilling({ notePath, label })}
        />
      ))}

      {drilling && !summary.weak_topics.some((t) => t.note_path === drilling.notePath) && (
        <QuizPanel
          notePath={drilling.notePath}
          label={drilling.label}
          onClose={() => setDrilling(null)}
          onScored={load}
        />
      )}
    </div>
  );
}

export default ProgressPage;
