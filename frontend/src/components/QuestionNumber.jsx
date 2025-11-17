export default function QuestionNumber({ question, value, onChange, error }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <p className="text-sm text-gray-500">{question.help_text}</p>
      )}
      
      <div className="relative">
        <input
          type="number"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={question.placeholder}
          min={question.validation?.min}
          max={question.validation?.max}
          step="0.01"
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          required={question.required}
        />
        {question.unite && (
          <span className="absolute right-3 top-2 text-gray-500">
            {question.unite}
          </span>
        )}
      </div>
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
