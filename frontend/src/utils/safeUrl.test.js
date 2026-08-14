import { describe, expect, it } from 'vitest'
import { safeHref } from './safeUrl'

describe('safeHref', () => {
  it('passes through http and https URLs unchanged', () => {
    expect(safeHref('https://example.com/article')).toBe('https://example.com/article')
    expect(safeHref('http://example.com/article')).toBe('http://example.com/article')
  })

  it('neutralizes a javascript: URI', () => {
    expect(safeHref('javascript:alert(document.cookie)')).toBe('#')
  })

  it('neutralizes a data: URI', () => {
    expect(safeHref('data:text/html,<script>alert(1)</script>')).toBe('#')
  })

  it('neutralizes an unparseable value', () => {
    expect(safeHref('not a url')).toBe('#')
    expect(safeHref('')).toBe('#')
    expect(safeHref(undefined)).toBe('#')
  })
})
