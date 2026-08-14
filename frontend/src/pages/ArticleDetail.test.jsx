import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ArticleDetail } from './ArticleDetail'
import { fetchArticle, recordArticleView } from '../api/articles'

vi.mock('../api/articles', () => ({
  fetchArticle: vi.fn(),
  recordArticleView: vi.fn(),
}))

vi.mock('../hooks/useToggleBookmark', () => ({
  useToggleBookmark: () => ({ toggle: vi.fn(), isLoading: false }),
}))

vi.mock('../hooks/useShareArticle', () => ({
  useShareArticle: () => ({ share: vi.fn() }),
}))

const ARTICLE = {
  id: 42,
  title: 'Some headline',
  summary: 'A summary',
  url: 'https://example.com/a',
  image_url: null,
  author: null,
  published_at: new Date().toISOString(),
  source: { name: 'Source' },
  category: { name: 'World' },
  is_bookmarked: false,
}

function renderDetail() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/article/42']}>
        <Routes>
          <Route path="/article/:id" element={<ArticleDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('ArticleDetail', () => {
  beforeEach(() => {
    fetchArticle.mockReset().mockResolvedValue(ARTICLE)
    recordArticleView.mockReset().mockResolvedValue(undefined)
  })

  it('records a view once the article id is known', async () => {
    renderDetail()

    await waitFor(() => expect(recordArticleView).toHaveBeenCalledWith('42'))
    await screen.findByText('Some headline')
  })

  it('does not let a failed view-tracking call break rendering', async () => {
    recordArticleView.mockRejectedValue(new Error('network error'))

    renderDetail()

    await screen.findByText('Some headline')
  })
})
