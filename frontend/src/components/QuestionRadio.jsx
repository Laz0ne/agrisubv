export default function QuestionRadio({ question, value, onChange, error }) {
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <p className="text-sm text-gray-500 mb-3">{question.help_text}</p>
      )}
      
      <div className="space-y-2">
        {question.options.map((option) => (
          <label
            key={option.value}
            className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
          >
            <input
              type="radio"
              name={question.id}
              checked={value === option.value}
              onChange={() => onChange(option.value)}
              className="w-4 h-4 text-green-600 border-gray-300 focus:ring-green-500"
            />
            <span className="text-sm text-gray-700">{option.label}</span>
          </label>
        ))}
      </div>
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
