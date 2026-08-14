import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { NotificationCategoryPicker } from './NotificationCategoryPicker'
import { fetchCategories } from '../api/articles'

vi.mock('../api/articles', () => ({ fetchCategories: vi.fn() }))

const CATEGORIES = [
  { id: 1, name: 'World', slug: 'world' },
  { id: 2, name: 'Tech', slug: 'tech' },
  { id: 3, name: 'Sports', slug: 'sports' },
]

function renderPicker(props) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <NotificationCategoryPicker {...props} />
    </QueryClientProvider>
  )
}

beforeEach(() => {
  fetchCategories.mockReset().mockResolvedValue(CATEGORIES)
})

describe('NotificationCategoryPicker', () => {
  it('marks "All categories" and every category as selected when categoryIds is null', async () => {
    renderPicker({ categoryIds: null, onChange: vi.fn() })

    await screen.findByText('Tech')
    expect(screen.getByText('All categories')).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('Tech')).toHaveAttribute('aria-pressed', 'true')
  })

  it('clicking a category while "all" is selected removes just that one', async () => {
    const onChange = vi.fn()
    renderPicker({ categoryIds: null, onChange })

    fireEvent.click(await screen.findByText('Tech'))

    expect(onChange).toHaveBeenCalledWith([1, 3])
  })

  it('clicking an unselected category adds it to an explicit list', async () => {
    const onChange = vi.fn()
    renderPicker({ categoryIds: [1], onChange })

    fireEvent.click(await screen.findByText('Sports'))

    expect(onChange).toHaveBeenCalledWith([1, 3])
  })

  it('clicking "All categories" resets to null', async () => {
    const onChange = vi.fn()
    renderPicker({ categoryIds: [1], onChange })

    fireEvent.click(await screen.findByText('All categories'))

    expect(onChange).toHaveBeenCalledWith(null)
  })
})
