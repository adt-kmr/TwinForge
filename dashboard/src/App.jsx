import React, { useEffect, useState } from "react";

// Same origin: vite proxies /ws/status to the orchestrator in dev (see vite.config.ts).
const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/status`;

/** Live job board. The orchestrator sends a snapshot on connect, then one message
 *  per job create/finish — so a plain upsert keyed by job_id is the whole state. */
export default function App() {
  const [jobs, setJobs] = useState({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let socket;
    let retry;
    const open = () => {
      socket = new WebSocket(WS_URL);
      socket.onopen = () => setConnected(true);
      socket.onmessage = (event) => {
        const job = JSON.parse(event.data);
        setJobs((prev) => ({ ...prev, [job.job_id]: job }));
      };
      socket.onclose = () => {
        setConnected(false);
        // The orchestrator restarts constantly during a demo; keep the board live.
        retry = setTimeout(open, 2000);
      };
    };
    open();
    return () => {
      clearTimeout(retry);
      if (socket) {
        socket.onclose = null;
        socket.close();
      }
    };
  }, []);

  const rows = Object.values(jobs);

  return (
    <>
      <h1>TwinForge pipeline</h1>
      <p className="sub">
        {connected ? "connected" : "reconnecting…"} · {rows.length} jobs
      </p>
      <table>
        <thead>
          <tr>
            <th>Stage</th>
            <th>Status</th>
            <th>Progress</th>
            <th>Detail</th>
            <th>Job</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((job) => (
            <tr key={job.job_id}>
              <td>{job.stage}</td>
              <td>
                <span className={`badge ${job.status}`}>{job.status}</span>
              </td>
              <td>{Math.round(job.progress * 100)}%</td>
              <td className="detail">
                {typeof job.detail === "string" ? job.detail : JSON.stringify(job.detail ?? "")}
              </td>
              <td className="detail">{job.job_id.slice(0, 8)}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td className="empty" colSpan={5}>
                No jobs yet — POST /reconstruct to start one.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </>
  );
}
