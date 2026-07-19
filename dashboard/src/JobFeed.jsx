import React, { useEffect, useState } from "react";

const WS_URL = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws/status`;

/** Live job board. The orchestrator sends a snapshot on connect, then one message per
 *  job create/finish — so a plain upsert keyed by job_id is the whole state. */
export default function JobFeed() {
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
        // The orchestrator gets restarted constantly during a demo; keep the feed live.
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

  const rows = Object.values(jobs).reverse();

  if (rows.length === 0) {
    return (
      <p className="hint">
        {connected ? "Waiting for the first job — run a stage." : "Reconnecting to the job stream…"}
      </p>
    );
  }

  return (
    <ul className="jobs">
      {rows.map((job) => (
        <li key={job.job_id} className={job.status}>
          <span className="stage-name">{job.stage}</span>
          <span className="status">{job.status}</span>
          <span className="detail">
            {typeof job.detail === "string" ? job.detail : JSON.stringify(job.detail ?? "")}
          </span>
        </li>
      ))}
    </ul>
  );
}
