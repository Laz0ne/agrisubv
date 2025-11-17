export default function QuestionSelect({ question, value, onChange, error }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <p className="text-sm text-gray-500">{question.help_text}</p>
      )}
      
      <select
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
        required={question.required}
      >
        <option value="">
          {question.placeholder || 'Sélectionnez une option'}
        </option>
        {question.options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
