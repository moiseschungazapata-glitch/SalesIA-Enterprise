import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Probability from '../src/modules/probability/Probability'

const analyticsMocks = vi.hoisted(() => ({
  calculateAutomaticBayes: vi.fn(),
}))

vi.mock('../src/services/analytics', () => ({
  analyzeRandomVariable: vi.fn(),
  calculateAutomaticBayes: analyticsMocks.calculateAutomaticBayes,
  calculateAutomaticEventProbability: vi.fn(),
}))

const automaticBayesResult = {
  analysis_id: 31,
  dataset_id: 28,
  dataset_name: 'Bayes automático - clientes recurrentes',
  analysis_type: 'bayes' as const,
  variable_name: null,
  variable_label: null,
  variable_type: null,
  observation_count: 10,
  results: [
    { metric: 'posterior', numeric_value: '0.60', text_value: null, details: {} },
    {
      metric: 'probability_a',
      numeric_value: '0.40',
      text_value: null,
      details: {},
    },
    {
      metric: 'probability_b_given_a',
      numeric_value: '0.75',
      text_value: null,
      details: {},
    },
    { metric: 'probability_b', numeric_value: '0.50', text_value: null, details: {} },
    { metric: 'universe_size', numeric_value: '10', text_value: null, details: {} },
    { metric: 'event_a_cases', numeric_value: '4', text_value: null, details: {} },
    { metric: 'event_b_cases', numeric_value: '5', text_value: null, details: {} },
    {
      metric: 'intersection_cases',
      numeric_value: '3',
      text_value: null,
      details: {},
    },
    {
      metric: 'interpretation',
      numeric_value: null,
      text_value:
        'El 60.00% de los clientes que compraron en el periodo acumuló al menos dos compras válidas hasta su cierre.',
      details: {},
    },
  ],
  created_at: '2026-10-15T13:00:00Z',
  completed_at: '2026-10-15T13:00:00Z',
}

describe('Bayes automático', () => {
  beforeEach(() => {
    analyticsMocks.calculateAutomaticBayes.mockReset()
  })

  it('consulta datos reales con el periodo elegido y presenta probabilidades y conteos', async () => {
    const user = userEvent.setup()
    analyticsMocks.calculateAutomaticBayes.mockResolvedValue(
      automaticBayesResult,
    )
    render(<Probability />)

    await user.click(screen.getByRole('button', { name: 'Bayes' }))

    expect(
      screen.getByRole('combobox', { name: 'Escenario bayesiano' }),
    ).toHaveValue('repeat_customer_given_purchase')
    expect(screen.queryByLabelText('P(A) · Previa')).not.toBeInTheDocument()
    expect(
      screen.getByText('Evento A · Cliente recurrente al cierre:'),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Cliente con al menos dos ventas confirmadas y no reembolsadas acumuladas/,
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/Las compras realizadas dentro del periodo también forman parte/),
    ).toBeInTheDocument()

    fireEvent.change(screen.getByLabelText('Desde (opcional)'), {
      target: { value: '2026-10-01' },
    })
    fireEvent.change(screen.getByLabelText('Hasta (opcional)'), {
      target: { value: '2026-10-15' },
    })
    await user.click(
      screen.getByRole('button', { name: 'Calcular' }),
    )

    await waitFor(() => {
      expect(analyticsMocks.calculateAutomaticBayes).toHaveBeenCalledWith({
        scenario_type: 'repeat_customer_given_purchase',
        date_from: '2026-10-01',
        date_to: '2026-10-15',
      })
    })

    expect(await screen.findByText('60.00%')).toBeInTheDocument()
    const probabilities = screen.getByLabelText('Probabilidades utilizadas')
    expect(within(probabilities).getByText('40.00%')).toBeInTheDocument()
    expect(within(probabilities).getByText('75.00%')).toBeInTheDocument()
    expect(within(probabilities).getByText('50.00%')).toBeInTheDocument()

    const counts = screen.getByLabelText('Conteos utilizados')
    expect(counts).toHaveTextContent('10 clientes en el universo')
    expect(counts).toHaveTextContent('4 recurrentes al cierre')
    expect(counts).toHaveTextContent('5 clientes que compraron en el periodo')
    expect(counts).toHaveTextContent(
      '3 recurrentes al cierre que compraron en el periodo',
    )
    expect(
      screen.getByText(/El 60.00% de los clientes que compraron/),
    ).toBeInTheDocument()
    expect(screen.getByText('Análisis #31 guardado')).toBeInTheDocument()
  })

  it('envía fechas nulas por defecto y muestra los errores de la API', async () => {
    const user = userEvent.setup()
    analyticsMocks.calculateAutomaticBayes.mockRejectedValue(
      new Error('No existen clientes para calcular este escenario.'),
    )
    render(<Probability />)

    await user.click(screen.getByRole('button', { name: 'Bayes' }))
    await user.click(
      screen.getByRole('button', { name: 'Calcular' }),
    )

    await waitFor(() => {
      expect(analyticsMocks.calculateAutomaticBayes).toHaveBeenCalledWith({
        scenario_type: 'repeat_customer_given_purchase',
        date_from: null,
        date_to: null,
      })
    })
    expect(
      await screen.findByText('No existen clientes para calcular este escenario.'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/Análisis #/)).not.toBeInTheDocument()
  })
})
