import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  viewName?: string;
}

interface State {
  hasError: boolean;
}

export default class SystemErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error caught in SystemErrorBoundary:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return <div>Something went wrong.</div>;
    }
    return this.props.children;
  }
}
