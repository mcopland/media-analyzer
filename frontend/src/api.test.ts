import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchMedia, fetchFilters, fetchMediaById } from './api'

const BASE = 'http://localhost:8000'

beforeEach(() => {
  vi.stubGlobal('import.meta', { env: { VITE_API_URL: BASE } })
})

describe('fetchFilters', () => {
  it('calls /api/filters', async () => {
    const mockData = { resolutions: ['1080p'], codecs: ['HEVC'], hdr: ['SDR'], containers: ['mkv'], audio_langs: ['eng'], sub_langs: [] }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => mockData }))
    const result = await fetchFilters()
    expect(fetch).toHaveBeenCalledWith(`${BASE}/api/filters`)
    expect(result).toEqual(mockData)
  })
})

describe('fetchMedia', () => {
  it('calls /api/media with no params', async () => {
    const mockData = { total: 0, items: [] }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => mockData }))
    const result = await fetchMedia({})
    expect((fetch as ReturnType<typeof vi.fn>).mock.calls[0][0]).toContain('/api/media')
    expect(result).toEqual(mockData)
  })

  it('includes limit and offset in URL', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total: 0, items: [] }) }))
    await fetchMedia({ limit: 25, offset: 50 })
    const url = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string
    expect(url).toContain('limit=25')
    expect(url).toContain('offset=50')
  })

  it('includes sort params in URL', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total: 0, items: [] }) }))
    await fetchMedia({ sortBy: 'filename', sortDir: 'desc' })
    const url = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string
    expect(url).toContain('sort_by=filename')
    expect(url).toContain('sort_dir=desc')
  })

  it('includes filter params in URL', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total: 0, items: [] }) }))
    await fetchMedia({ codec: 'HEVC', resolution: '1080p', hdr: 'HDR10' })
    const url = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string
    expect(url).toContain('codec=HEVC')
    expect(url).toContain('resolution=1080p')
    expect(url).toContain('hdr=HDR10')
  })

  it('omits empty filter params', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ total: 0, items: [] }) }))
    await fetchMedia({ codec: '', resolution: undefined })
    const url = (fetch as ReturnType<typeof vi.fn>).mock.calls[0][0] as string
    expect(url).not.toContain('codec=')
    expect(url).not.toContain('resolution=')
  })
})

describe('fetchMediaById', () => {
  it('calls /api/media/:id', async () => {
    const mockItem = { id: 42, filename: 'foo.mkv', audio_tracks: [], subtitle_tracks: [] }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => mockItem }))
    const result = await fetchMediaById(42)
    expect((fetch as ReturnType<typeof vi.fn>).mock.calls[0][0]).toBe(`${BASE}/api/media/42`)
    expect(result).toEqual(mockItem)
  })
})
