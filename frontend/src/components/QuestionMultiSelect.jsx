export default function QuestionMultiSelect({ question, value = [], onChange, error }) {
  const handleToggle = (optionValue) => {
    const newValue = value.includes(optionValue)
      ? value.filter(v => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  const handleKeyDown = (e, optionValue) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleToggle(optionValue);
    }
  };

  return (
    <div className="space-y-3 animate-fade-in">
      <label className="input-label">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <div className="flex items-start gap-2 p-3 bg-gradient-to-r from-blue-50 to-cyan-50 border border-blue-100 rounded-xl">
          <span className="text-blue-500 text-lg" aria-hidden="true">💡</span>
          <p className="text-sm text-blue-700">{question.help_text}</p>
        </div>
      )}
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3" role="group" aria-label={question.label}>
        {question.options?.map((option, index) => {
          const isSelected = value.includes(option.value);
          const delayClass = `animation-delay-${Math.min(index * 50, 500)}`;
          return (
            <div
              key={option.value}
              onClick={() => handleToggle(option.value)}
              onKeyDown={(e) => handleKeyDown(e, option.value)}
              className={`select-card ${isSelected ? 'selected' : ''} ${delayClass}`}
              role="checkbox"
              aria-checked={isSelected}
              tabIndex={0}
            >
              <div className="select-card-checkbox">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" aria-hidden="true">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              
              {option.icon && (
                <span className="select-card-icon" aria-hidden="true">{option.icon}</span>
              )}
              
              <span className="select-card-label">{option.label}</span>
            </div>
          );
        })}
      </div>
      
      {value.length > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <span className="badge badge-success">
            ✓ {value.length} sélectionné{value.length > 1 ? 's' : ''}
          </span>
        </div>
      )}
      
      {error && (
        <p className="input-error">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
