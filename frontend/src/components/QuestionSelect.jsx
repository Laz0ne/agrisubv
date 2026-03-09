export default function QuestionSelect({ question, value, onChange, error }) {
  return (
    <div className="space-y-2 animate-fade-in">
      <label className="input-label" htmlFor={`q-${question.id}`}>
        {question.label}
        {question.required && <span className="text-red-500 ml-1" aria-hidden="true">*</span>}
        {question.required && <span className="sr-only">(obligatoire)</span>}
      </label>

      {question.help_text && (
        <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-100 rounded-xl">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-500 flex-shrink-0 mt-0.5" aria-hidden="true">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <p className="text-sm text-blue-700">{question.help_text}</p>
        </div>
      )}

      <select
        id={`q-${question.id}`}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        required={question.required}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={error ? `err-${question.id}` : undefined}
        className={`input-modern ${error ? 'has-error' : ''}`}
      >
        <option value="">{question.placeholder || 'Sélectionnez…'}</option>
        {question.options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

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
