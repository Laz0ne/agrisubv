export default function QuestionRadio({ question, value, onChange, error }) {
  return (
    <div className="space-y-3 animate-fade-in">
      <label className="input-label">
        {question.label}
        {question.required && <span className="text-red-500 ml-1" aria-hidden="true">*</span>}
        {question.required && <span className="sr-only">(obligatoire)</span>}
      </label>

      {question.help_text && (
        <p className="text-sm text-gray-500 bg-blue-50 border border-blue-100 p-2 rounded-lg">{question.help_text}</p>
      )}

      <div className="space-y-2" role="radiogroup" aria-label={question.label}>
        {question.options.map((option) => {
          const isChecked = value === option.value;
          return (
            <label
              key={option.value}
              className={`flex items-center gap-3 p-3.5 border-2 rounded-xl cursor-pointer transition-all duration-200 ${
                isChecked
                  ? 'border-green-500 bg-green-50 shadow-sm'
                  : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              {/* Custom radio */}
              <div
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                  isChecked ? 'border-green-500 bg-green-500' : 'border-gray-300 bg-white'
                }`}
                aria-hidden="true"
              >
                {isChecked && (
                  <div className="w-2 h-2 rounded-full bg-white"></div>
                )}
              </div>
              <input
                type="radio"
                name={question.id}
                value={String(option.value)}
                checked={isChecked}
                onChange={() => onChange(option.value)}
                className="sr-only"
              />
              <span className={`text-sm font-medium ${isChecked ? 'text-green-800' : 'text-gray-700'}`}>
                {option.label}
              </span>
            </label>
          );
        })}
      </div>

      {error && (
        <p className="input-error" role="alert">
          <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
