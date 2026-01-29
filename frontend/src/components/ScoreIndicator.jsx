export default function ScoreIndicator({ score, size = 60, eligible }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  
  const color = eligible ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444';
  const scoreValue = Math.round(score);
  const ariaLabel = `Score d'éligibilité: ${scoreValue} sur 100${eligible ? ', éligible' : score >= 40 ? ', presque éligible' : ', non éligible'}`;
  
  return (
    <div className="score-ring" style={{ width: size, height: size }} aria-label={ariaLabel} role="img">
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
        />
      </svg>
      <div className="score-ring-text" style={{ color }} aria-hidden="true">
        {scoreValue}
      </div>
    </div>
  );
}
