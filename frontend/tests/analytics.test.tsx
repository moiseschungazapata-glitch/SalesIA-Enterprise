import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Analytics from '../src/modules/analytics/Analytics'

const analyticsMocks = vi.hoisted(() => ({ reload: vi.fn() }))

vi.mock('../src/hooks/useAnalytics', () => ({
  useAnalyticsMetadata: () => ({
    variables: [
      {
        name: 'sale_total',
        label: 'Monto total de venta',
        variable_type: 'quantitative_continuous',
        data_type: 'decimal',
        unit: 'PEN',
        description: 'Importe final de cada venta confirmada.',
      },
    ],
    history: {
      items: [
        {
          analysis_id: 24,
          dataset_id: 24,
          dataset_name: 'Dataset automático de prueba',
          analysis_type: 'frequency',
          variable_name: 'order_converted',
          variable_label: 'Pedido convertido en venta',
          variable_type: 'quantitative_discrete',
          observation_count: 5,
          results: [],
          created_at: '2026-10-15T12:55:43Z',
          completed_at: '2026-10-15T12:55:43Z',
          status: 'completed',
          parameters: {},
        },
      ],
      total: 1,
      page: 1,
      page_size: 50,
    },
    loading: false,
    error: '',
    reload: analyticsMocks.reload,
  }),
}))

describe('secciones de Analytics', () => {
  it('mantiene el historial oculto hasta seleccionar su pestaña', async () => {
    const user = userEvent.setup()
    render(<Analytics />)

    expect(screen.getByText('Analizar ventas confirmadas')).toBeInTheDocument()
    expect(screen.queryByText('Dataset automático de prueba')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Historial de análisis: 1 registros' }))

    expect(screen.getByText('Dataset automático de prueba')).toBeInTheDocument()
    expect(screen.queryByText('Analizar ventas confirmadas')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Nuevo análisis' }))

    expect(screen.getByText('Analizar ventas confirmadas')).toBeInTheDocument()
    expect(screen.queryByText('Dataset automático de prueba')).not.toBeInTheDocument()
  })
})
