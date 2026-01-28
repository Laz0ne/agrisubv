export default function QuestionSelect({ question, value, onChange, error }) {
  return (
    <div className="space-y-2 animate-fade-in">
      <label className="block text-sm font-semibold text-gray-700">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <p className="text-sm text-gray-500 bg-blue-50 p-2 rounded-lg">{question.help_text}</p>
      )}
      
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className={`input-modern ${error ? 'border-red-500 focus:border-red-500' : ''}`}
      >
        <option value="">{question.placeholder || 'Sélectionnez...'}</option>
        {question.options?.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="text-sm text-red-600 flex items-center gap-1">
          <span>⚠️</span> {error}
        </p>
      )}
    </div>
  );
}
