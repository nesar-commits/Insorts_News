import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { HeroCarousel } from './HeroCarousel'

function makeArticle(id) {
  return {
    id,
    title: `Article ${id}`,
    image_url: null,
    published_at: new Date().toISOString(),
    category: { name: 'World', icon: 'globe' },
    source: { name: 'Source' },
  }
}

function renderCarousel(articles) {
  return render(
    <MemoryRouter>
      <HeroCarousel articles={articles} />
    </MemoryRouter>
  )
}

describe('HeroCarousel', () => {
  it('renders nothing for an empty list', () => {
    const { container } = renderCarousel([])
    expect(container).toBeEmptyDOMElement()
  })

  it('renders the slide at the current index', () => {
    renderCarousel([makeArticle(1), makeArticle(2)])
    expect(screen.getByText('Article 1')).toBeInTheDocument()
  })

  it('does not crash when the array shrinks below the current slide index', () => {
    const six = Array.from({ length: 6 }, (_, i) => makeArticle(i + 1))
    const { rerender } = renderCarousel(six)

    // Jump to the last slide (index 5) via its dot indicator.
    fireEvent.click(screen.getByLabelText('Go to slide 6'))
    expect(screen.getByText('Article 6')).toBeInTheDocument()

    // Simulate the ['trending'] query refetching a shorter list while
    // mounted (e.g. after any bookmark toggle elsewhere invalidates it).
    const three = Array.from({ length: 3 }, (_, i) => makeArticle(i + 1))
    expect(() =>
      rerender(
        <MemoryRouter>
          <HeroCarousel articles={three} />
        </MemoryRouter>
      )
    ).not.toThrow()

    // Clamped to the new last slide instead of indexing out of bounds.
    expect(screen.getByText('Article 3')).toBeInTheDocument()
  })
})
