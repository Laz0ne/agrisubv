export default function QuestionNumber({ question, value, onChange, error }) {
  return (
    <div className="space-y-2 animate-fade-in">
      <label className="input-label" htmlFor={`q-${question.id}`}>
        {question.label}
        {question.required && <span className="text-red-500 ml-1" aria-hidden="true">*</span>}
        {question.required && <span className="sr-only">(obligatoire)</span>}
      </label>

      {question.help_text && (
        <p className="text-sm text-gray-500">{question.help_text}</p>
      )}

      <div className="relative">
        <input
          id={`q-${question.id}`}
          type="number"
          value={value || ''}
          onChange={(e) => onChange(e.target.value ? parseFloat(e.target.value) : null)}
          placeholder={question.placeholder}
          min={question.validation?.min}
          max={question.validation?.max}
          step="0.01"
          required={question.required}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? `err-${question.id}` : undefined}
          className={`input-modern pr-14 ${error ? 'has-error' : ''}`}
        />
        {question.unite && (
          <span
            className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-gray-400 pointer-events-none"
            aria-hidden="true"
          >
            {question.unite}
          </span>
        )}
      </div>

      {error && (
        <p id={`err-${question.id}`} className="input-error" role="alert">
          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
