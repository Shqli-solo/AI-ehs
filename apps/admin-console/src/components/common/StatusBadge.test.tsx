import * as React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '@/components/common/StatusBadge';

describe('StatusBadge - Risk Level', () => {
  it('应该显示"低"等级', () => {
    render(<StatusBadge type="risk" value="low" />);
    expect(screen.getByText('低')).toBeInTheDocument();
  });

  it('应该显示"中"等级', () => {
    render(<StatusBadge type="risk" value="medium" />);
    expect(screen.getByText('中')).toBeInTheDocument();
  });

  it('应该显示"高"等级', () => {
    render(<StatusBadge type="risk" value="high" />);
    expect(screen.getByText('高')).toBeInTheDocument();
  });

  it('应该显示"严重"等级', () => {
    render(<StatusBadge type="risk" value="critical" />);
    expect(screen.getByText('严重')).toBeInTheDocument();
  });

  it('应该为低风险使用绿色样式', () => {
    const { container } = render(<StatusBadge type="risk" value="low" />);
    expect(container.firstChild).toHaveClass('bg-green-100');
  });

  it('应该为高风险使用橙色样式', () => {
    const { container } = render(<StatusBadge type="risk" value="high" />);
    expect(container.firstChild).toHaveClass('bg-orange-100');
  });

  it('应该为严重风险使用红色样式', () => {
    const { container } = render(<StatusBadge type="risk" value="critical" />);
    expect(container.firstChild).toHaveClass('bg-red-100');
  });

  it('应该为未知等级使用灰色样式', () => {
    const { container } = render(<StatusBadge type="risk" value="unknown" />);
    expect(container.firstChild).toHaveClass('bg-gray-100');
  });
});

describe('StatusBadge - Status', () => {
  it('应该显示"待处理"', () => {
    render(<StatusBadge type="status" value="pending" />);
    expect(screen.getByText('待处理')).toBeInTheDocument();
  });

  it('应该显示"处理中"', () => {
    render(<StatusBadge type="status" value="processing" />);
    expect(screen.getByText('处理中')).toBeInTheDocument();
  });

  it('应该显示"已解决"', () => {
    render(<StatusBadge type="status" value="resolved" />);
    expect(screen.getByText('已解决')).toBeInTheDocument();
  });

  it('应该为待处理使用橙色样式', () => {
    const { container } = render(<StatusBadge type="status" value="pending" />);
    expect(container.firstChild).toHaveClass('bg-orange-100');
  });

  it('应该为处理中使用蓝色样式', () => {
    const { container } = render(<StatusBadge type="status" value="processing" />);
    expect(container.firstChild).toHaveClass('bg-blue-100');
  });

  it('应该为已解决使用绿色样式', () => {
    const { container } = render(<StatusBadge type="status" value="resolved" />);
    expect(container.firstChild).toHaveClass('bg-green-100');
  });

  it('应该为未知状态回退显示原值', () => {
    render(<StatusBadge type="status" value="unknown" />);
    expect(screen.getByText('unknown')).toBeInTheDocument();
  });
});

describe('StatusBadge - Device', () => {
  it('应该显示设备类型值', () => {
    render(<StatusBadge type="device" value="smoke_detector" />);
    expect(screen.getByText('smoke_detector')).toBeInTheDocument();
  });
});
