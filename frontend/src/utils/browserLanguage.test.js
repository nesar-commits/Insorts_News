import { afterEach, describe, expect, it } from 'vitest'
import { getBrowserLanguage } from './browserLanguage'

describe('getBrowserLanguage', () => {
  const originalNavigatorLanguage = navigator.language
  const originalNavigatorLanguages = navigator.languages

  afterEach(() => {
    Object.defineProperty(navigator, 'language', {
      value: originalNavigatorLanguage,
      configurable: true,
    })
    Object.defineProperty(navigator, 'languages', {
      value: originalNavigatorLanguages,
      configurable: true,
    })
  })

  function setLanguage(lang, langs) {
    Object.defineProperty(navigator, 'language', {
      value: lang,
      configurable: true,
    })
    Object.defineProperty(navigator, 'languages', {
      value: langs || (lang ? [lang] : []),
      configurable: true,
    })
  }

  it('correctly handles hyphenated locales like en-US and hi-IN', () => {
    setLanguage('en-US')
    expect(getBrowserLanguage()).toBe('en')

    setLanguage('hi-IN')
    expect(getBrowserLanguage()).toBe('hi')
  })

  it('correctly handles underscore-delimited locales like en_US and zh_CN', () => {
    setLanguage('en_US')
    expect(getBrowserLanguage()).toBe('en')

    setLanguage('zh_CN')
    expect(getBrowserLanguage()).toBe('zh')

    setLanguage('pt_BR')
    expect(getBrowserLanguage()).toBe('pt')
  })

  it('returns null when no language is defined', () => {
    setLanguage('', [])
    expect(getBrowserLanguage()).toBeNull()
  })

  it('clamps language code to 3 characters max', () => {
    setLanguage('eng-US')
    expect(getBrowserLanguage()).toBe('eng')
  })
})
