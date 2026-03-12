import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import RowDetail from './RowDetail'
import type { MediaItem } from '../api'

const item: MediaItem = {
  id: 1,
  filename: 'movie.mkv',
  path: '/media/movies/movie.mkv',
  size_bytes: 5_000_000_000,
  mtime: 1000,
  duration_secs: 7200,
  width: 3840,
  height: 2160,
  fps: 23.976,
  video_codec: 'HEVC',
  video_bitrate_kbps: 15000,
  overall_bitrate_kbps: 16000,
  hdr: 'HDR10',
  container: 'mkv',
  scanned_at: '2026-01-01T00:00:00Z',
  audio_tracks: [
    { id: 1, media_id: 1, track_index: 0, codec: 'truehd', channels: 8, language: 'eng', is_default: true },
    { id: 2, media_id: 1, track_index: 1, codec: 'ac3', channels: 6, language: 'fra', is_default: false },
  ],
  subtitle_tracks: [
    { id: 3, media_id: 1, track_index: 2, codec: 'subrip', language: 'eng', forced: false, is_default: true },
    { id: 4, media_id: 1, track_index: 3, codec: 'subrip', language: 'fra', forced: true, is_default: false },
  ],
}

describe('RowDetail', () => {
  it('renders the full path', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText('/media/movies/movie.mkv')).toBeInTheDocument()
  })

  it('renders audio track codec and language', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText('truehd')).toBeInTheDocument()
    expect(screen.getByText('ac3')).toBeInTheDocument()
    expect(screen.getAllByText('eng').length).toBeGreaterThan(0)
    expect(screen.getAllByText('fra').length).toBeGreaterThan(0)
  })

  it('renders audio track channel count', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText('8')).toBeInTheDocument()
  })

  it('renders subtitle tracks', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText('subrip')).toBeInTheDocument()
  })

  it('shows forced indicator for forced subtitle', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText(/forced/i)).toBeInTheDocument()
  })

  it('renders with no audio tracks', () => {
    const noAudio = { ...item, audio_tracks: [] }
    render(<RowDetail item={noAudio} />)
    expect(screen.getByText('/media/movies/movie.mkv')).toBeInTheDocument()
  })

  it('renders with no subtitle tracks', () => {
    const noSubs = { ...item, subtitle_tracks: [] }
    render(<RowDetail item={noSubs} />)
    expect(screen.getByText('/media/movies/movie.mkv')).toBeInTheDocument()
  })

  it('renders duration', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText(/2:00:00|7200|120/i)).toBeInTheDocument()
  })

  it('renders video codec', () => {
    render(<RowDetail item={item} />)
    expect(screen.getByText('HEVC')).toBeInTheDocument()
  })
})
