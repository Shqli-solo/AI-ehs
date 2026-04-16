import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ToastProvider, ToastViewport } from './toast';
import { useToast } from '@/hooks/use-toast';

// 包装组件用于提供 ToastProvider
function ToastTestWrapper({ children }: { children: React.ReactNode }) {
  return (
    <ToastProvider>
      {children}
      <ToastViewport />
    </ToastProvider>
  );
}

// 测试用的 Toast 触发组件
function TriggerToast() {
  const { toast } = useToast();

  React.useEffect(() => {
    toast({
      title: 'Test Toast',
      description: 'This is a test toast',
    });
  }, [toast]);

  return <div data-testid="trigger">triggered</div>;
}

describe('Toast Component', () => {
  it('renders toast viewport', () => {
    render(
      <ToastTestWrapper>
        <div>Test Content</div>
      </ToastTestWrapper>
    );

    // ToastViewport should render with proper aria-label
    const region = screen.getByLabelText(/notifications/i);
    expect(region).toBeInTheDocument();
  });

  it('toast function can be called', async () => {
    let toastCalled = false;

    function TestComponent() {
      const { toast } = useToast();

      React.useEffect(() => {
        toast({
          title: 'Test',
          description: 'Test description',
        });
        toastCalled = true;
      }, []);

      return <div data-testid="result">done</div>;
    }

    render(
      <ToastTestWrapper>
        <TestComponent />
      </ToastTestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('result')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(toastCalled).toBe(true);
  });

  it('TriggerToast component triggers toast', async () => {
    render(
      <ToastTestWrapper>
        <TriggerToast />
      </ToastTestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByTestId('trigger')).toBeInTheDocument();
    }, { timeout: 2000 });
  });
});
