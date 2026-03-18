import { Component } from 'react';

/**
 * Error boundary that catches unhandled render errors in the questionnaire
 * and results pages, preventing the entire app from going blank.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('ErrorBoundary caught:', error, info);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    if (this.props.onReset) this.props.onReset();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-3xl mx-auto px-4 py-16 text-center">
          <div className="card p-8">
            <div className="text-5xl mb-4" aria-hidden="true">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Une erreur inattendue est survenue
            </h2>
            <p className="text-gray-600 mb-6">
              {this.props.fallbackMessage ||
                "Le questionnaire a rencontré un problème. Veuillez réessayer."}
            </p>
            <button
              onClick={this.handleReset}
              className="btn btn-primary mx-auto"
            >
              Réessayer
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
