import { render, screen } from '@testing-library/react';
import App from './App';

test('renders nse pulse title', () => {
  render(<App />);
  const linkElement = screen.getByText(/NSE Pulse/i);
  expect(linkElement).toBeInTheDocument();
});
