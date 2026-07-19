import React, { useState } from "react";

const MODEL_OPTIONS = [
  {
    key: "geometry-only",
    label: "Geometry-Only",
    description: "Voxel clustering with structural heuristics, no ML weights",
  },
  {
    key: "yolo-world",
    label: "YOLO-World",
    description: "Enhanced image segmentation for richer semantic labeling",
  },
];

export default function ModelStep({ onNext }) {
  const [selected, setSelected] = useState(null);

  const handleSelect = (key) => {
    setSelected(key);
    onNext({ modelChoice: key });
  };

  return (
    <div className="wizard__step">
      <h2>Choose a semantic model</h2>
      <p className="prose">
        Select the perception backend for twin labeling. Geometry-only is fast and works
        offline; YOLO-World adds visual understanding when available.
      </p>

      <div className="model-options">
        {MODEL_OPTIONS.map((option) => (
          <button
            key={option.key}
            className={`model-option ${selected === option.key ? "is-selected" : ""}`}
            onClick={() => handleSelect(option.key)}
          >
            <strong>{option.label}</strong>
            <p>{option.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
