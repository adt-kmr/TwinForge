import React, { useState } from "react";

import * as api from "../../api.js";

// Small, non-exhaustive list -- matches FunctionGemmaPlanner/SarvamPlanner's lang param,
// doesn't need to be exhaustive for this milestone.
const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ta", label: "Tamil" },
  { code: "te", label: "Telugu" },
];

/**
 * Audio -> task graph, in two calls: POST /transcribe (audio -> text, Whisper-only,
 * independent of SARVAM_API_KEY) then the existing POST /plan (text -> task graph,
 * already picks Sarvam-online vs. FunctionGemma-offline). No second new codepath.
 *
 * Live microphone capture (MediaRecorder/getUserMedia) needs real browser permissions
 * this environment can't exercise (same constraint Task 16 hit for capture) -- a file
 * input for a pre-recorded clip is the honest, buildable scope here.
 */
export default function VoiceStep({ state, onNext }) {
  const [lang, setLang] = useState(state.lang || "en");
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      const { text } = await api.transcribe(file, lang);
      const planned = await api.plan(state.twinId, text, lang);
      onNext({ taskText: text, lang, taskGraphId: planned.task_graph_id });
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="wizard__step">
      <h2>Say the task</h2>
      <p className="prose">
        Pick a language and an audio clip with the instruction. We'll transcribe it and
        turn it into a task graph.
      </p>

      <label>
        Language
        <select value={lang} onChange={(e) => setLang(e.target.value)} disabled={busy}>
          {LANGUAGES.map(({ code, label }) => (
            <option key={code} value={code}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <label>
        Audio clip
        <input
          type="file"
          accept="audio/*"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          disabled={busy}
        />
      </label>

      <button className="btn btn--solid" onClick={run} disabled={busy || !file}>
        {busy ? "Transcribing…" : "Continue"}
      </button>

      {error && (
        <div className="error">
          <strong>{error.message}</strong>
          {typeof error.detail === "object" && error.detail !== null && (
            <dl>
              {Object.entries(error.detail)
                .filter(([key]) => key !== "error")
                .map(([key, value]) => (
                  <React.Fragment key={key}>
                    <dt>{key.replace(/_/g, " ")}</dt>
                    <dd>{String(value)}</dd>
                  </React.Fragment>
                ))}
            </dl>
          )}
        </div>
      )}
    </div>
  );
}
