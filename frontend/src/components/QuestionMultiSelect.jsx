export default function QuestionMultiSelect({ question, value = [], onChange, error }) {
  const handleToggle = (optionValue) => {
    const newValue = value.includes(optionValue)
      ? value.filter(v => v !== optionValue)
      : [...value, optionValue];
    onChange(newValue);
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {question.label}
        {question.required && <span className="text-red-500 ml-1">*</span>}
      </label>
      
      {question.help_text && (
        <p className="text-sm text-gray-500">{question.help_text}</p>
      )}
      
      <div className="space-y-2 max-h-64 overflow-y-auto border border-gray-200 rounded-lg p-3">
        {question.options.map((option) => (
          <label
            key={option.value}
            className="flex items-center space-x-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={value.includes(option.value)}
              onChange={() => handleToggle(option.value)}
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <span className="text-sm text-gray-700">
              {option.icon && <span className="mr-2">{option.icon}</span>}
              {option.label}
            </span>
          </label>
        ))}
      </div>
      
      {value.length > 0 && (
        <p className="text-xs text-gray-500">
          {value.length} sélection(s)
        </p>
      )}
      
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
}
