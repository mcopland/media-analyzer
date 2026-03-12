import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MediaTable from './MediaTable'
import type { MediaItem } from '../api'

const makeItem = (id: number, filename: string): MediaItem => ({
  id,
  filename,
  path: `/media/${filename}`,
  size_bytes: 1_000_000_000,
  mtime: 1000,
  duration_secs: 3600,
  width: 1920,
  height: 1080,
  fps: 23.976,
  video_codec: 'HEVC',
  video_bitrate_kbps: 5000,
  overall_bitrate_kbps: 6000,
  hdr: 'HDR10',
  container: 'mkv',
  scanned_at: '2026-01-01T00:00:00Z',
  audio_tracks: [{ id: 1, media_id: id, track_index: 0, codec: 'aac', channels: 2, language: 'eng', is_default: true }],
  subtitle_tracks: [],
})

const items = [makeItem(1, 'aaa.mkv'), makeItem(2, 'bbb.mkv'), makeItem(3, 'ccc.mkv')]

describe('MediaTable', () => {
  it('renders rows for each item', () => {
    render(
      <MediaTable
        items={items}
        total={3}
        sortBy="filename"
        sortDir="asc"
        onSort={vi.fn()}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    expect(screen.getByText('aaa.mkv')).toBeInTheDocument()
    expect(screen.getByText('bbb.mkv')).toBeInTheDocument()
    expect(screen.getByText('ccc.mkv')).toBeInTheDocument()
  })

  it('calls onSort when filename header clicked', () => {
    const onSort = vi.fn()
    render(
      <MediaTable
        items={items}
        total={3}
        sortBy="filename"
        sortDir="asc"
        onSort={onSort}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByText(/filename/i))
    expect(onSort).toHaveBeenCalledWith('filename', 'desc')
  })

  it('toggles sort direction on second click', () => {
    const onSort = vi.fn()
    render(
      <MediaTable
        items={items}
        total={3}
        sortBy="filename"
        sortDir="desc"
        onSort={onSort}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByText(/filename/i))
    expect(onSort).toHaveBeenCalledWith('filename', 'asc')
  })

  it('expands row detail on row click', () => {
    render(
      <MediaTable
        items={items}
        total={3}
        sortBy="filename"
        sortDir="asc"
        onSort={vi.fn()}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByText('aaa.mkv'))
    expect(screen.getByText('/media/aaa.mkv')).toBeInTheDocument()
  })

  it('collapses row detail on second click', () => {
    render(
      <MediaTable
        items={items}
        total={3}
        sortBy="filename"
        sortDir="asc"
        onSort={vi.fn()}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    fireEvent.click(screen.getByText('aaa.mkv'))
    fireEvent.click(screen.getByText('aaa.mkv'))
    expect(screen.queryByText('/media/aaa.mkv')).not.toBeInTheDocument()
  })

  it('shows pagination controls', () => {
    render(
      <MediaTable
        items={items}
        total={30}
        sortBy="filename"
        sortDir="asc"
        onSort={vi.fn()}
        limit={10}
        offset={0}
        onPageChange={vi.fn()}
      />,
    )
    expect(screen.getByText(/next/i)).toBeInTheDocument()
  })

  it('calls onPageChange when next page clicked', () => {
    const onPageChange = vi.fn()
    render(
      <MediaTable
        items={items}
        total={30}
        sortBy="filename"
        sortDir="asc"
        onSort={vi.fn()}
        limit={10}
        offset={0}
        onPageChange={onPageChange}
      />,
    )
    fireEvent.click(screen.getByText(/next/i))
    expect(onPageChange).toHaveBeenCalledWith(10, 10)
  })
})
