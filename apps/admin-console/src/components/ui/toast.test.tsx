import * as React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ToastProvider, Toast, ToastTitle, ToastDescription, ToastClose, ToastViewport } from './toast';
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
function TriggerToast({ variant = 'default' }: { variant?: string }) {
  const { toast } = useToast();

  React.useEffect(() => {
    toast({
      variant: variant as any,
      title: 'Test Toast',
      description: 'This is a test toast',
    });
  }, [toast]);

  return <div data-testid="trigger">triggered</div>;
}

describe('Toast Component', () => {
  describe('Rendering', () => {
    it('renders toast with title', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast />
        </ToastTestWrapper>
      );

      expect(screen.getByTestId('trigger')).toBeInTheDocument();

      // Wait for toast to appear
      await waitFor(() => {
        const toastElement = screen.getByText('Test Toast');
        expect(toastElement).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('renders toast with description', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('This is a test toast')).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('renders toast with success variant', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast variant="success" />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        const toastElement = screen.getByText('Test Toast');
        expect(toastElement).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('renders toast with destructive variant', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast variant="destructive" />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        const toastElement = screen.getByText('Test Toast');
        expect(toastElement).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('renders toast with info variant', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast variant="info" />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        const toastElement = screen.getByText('Test Toast');
        expect(toastElement).toBeInTheDocument();
      }, { timeout: 2000 });
    });

    it('renders toast with warning variant', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast variant="warning" />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        const toastElement = screen.getByText('Test Toast');
        expect(toastElement).toBeInTheDocument();
      }, { timeout: 2000 });
    });
  });

  describe('Toast Close', () => {
    it('has close button', async () => {
      render(
        <ToastTestWrapper>
          <TriggerToast />
        </ToastTestWrapper>
      );

      await waitFor(() => {
        const closeButton = screen.getByRole('button', { name: /close/i });
        expect(closeButton).toBeInTheDocument();
      }, { timeout: 2000 });
    });
  });

  describe('useToast Hook', () => {
    it('toast function returns id and dismiss', async () => {
      let toastResult: ReturnType<typeof useToast['toast']> | null = null;

      function TestComponent() {
        const { toast } = useToast();

        React.useEffect(() => {
          toastResult = toast({
            title: 'Test',
            description: 'Test description',
          });
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

      expect(toastResult).toBeTruthy();
      expect(toastResult?.id).toBeDefined();
      expect(toastResult?.dismiss).toBeDefined();
    });
  });
});
