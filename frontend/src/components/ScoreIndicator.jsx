import { useEffect, useState } from 'react';

export default function ScoreIndicator({ score, size = 60, eligible }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  // Animate the stroke-dashoffset on mount
  useEffect(() => {
    const t = setTimeout(() => setAnimatedScore(score), 100);
    return () => clearTimeout(t);
  }, [score]);

  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedScore / 100) * circumference;

  const color = eligible ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';
  const scoreValue = Math.round(score);
  const ariaLabel = `Score d'éligibilité: ${scoreValue} sur 100${eligible ? ', éligible' : score >= 40 ? ', presque éligible' : ', non éligible'}`;

  return (
    <div
      className="score-ring"
      style={{ width: size, height: size }}
      aria-label={ariaLabel}
      role="img"
    >
      <svg width={size} height={size} aria-hidden="true">
        <circle
          className="score-ring-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
        />
        <circle
          className="score-ring-progress"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
        />
      </svg>
      <div className="score-ring-text" style={{ color }} aria-hidden="true">
        {scoreValue}
      </div>
    </div>
  );
}
