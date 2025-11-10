
  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await apiCall();
      // Log the backend response for debugging
      console.log('Backend response:', response.data);
      const aides = response.data.aides_eligibles || [];
      setResults({ aidesEligibles: aides, loading: false, error: '' });
    } catch (error) {
      console.error('Error:', error);
      setResults({ aidesEligibles: [], loading: false, error: 'An error occurred' });
    }
  };