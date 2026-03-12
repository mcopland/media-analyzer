import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FilterBar from './FilterBar'
import type { Filters } from '../api'

const filters: Filters = {
  resolutions: ['720p', '1080p', '2160p'],
  codecs: ['H264', 'HEVC'],
  hdr: ['SDR', 'HDR10'],
  containers: ['mkv', 'mp4'],
  audio_langs: ['eng', 'fra'],
  sub_langs: ['eng'],
}

const noFilters: Filters = {
  resolutions: [],
  codecs: [],
  hdr: [],
  containers: [],
  audio_langs: [],
  sub_langs: [],
}

describe('FilterBar', () => {
  it('renders without crashing when no filters', () => {
    render(<FilterBar filters={noFilters} values={{}} onChange={vi.fn()} />)
  })

  it('renders resolution options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All resolutions')).toBeInTheDocument()
  })

  it('renders codec options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All codecs')).toBeInTheDocument()
  })

  it('renders HDR options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All HDR')).toBeInTheDocument()
  })

  it('renders container options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All containers')).toBeInTheDocument()
  })

  it('renders audio lang options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All audio langs')).toBeInTheDocument()
  })

  it('renders sub lang options', () => {
    render(<FilterBar filters={filters} values={{}} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('All sub langs')).toBeInTheDocument()
  })

  it('calls onChange when resolution selected', () => {
    const onChange = vi.fn()
    render(<FilterBar filters={filters} values={{}} onChange={onChange} />)
    const select = screen.getByDisplayValue('All resolutions')
    fireEvent.change(select, { target: { value: '1080p' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ resolution: '1080p' }))
  })

  it('calls onChange when codec selected', () => {
    const onChange = vi.fn()
    render(<FilterBar filters={filters} values={{}} onChange={onChange} />)
    const select = screen.getByDisplayValue('All codecs')
    fireEvent.change(select, { target: { value: 'HEVC' } })
    expect(onChange).toHaveBeenCalledWith(expect.objectContaining({ codec: 'HEVC' }))
  })

  it('shows current filter values in selects', () => {
    render(<FilterBar filters={filters} values={{ resolution: '1080p', codec: 'HEVC' }} onChange={vi.fn()} />)
    expect(screen.getByDisplayValue('1080p')).toBeInTheDocument()
    expect(screen.getByDisplayValue('HEVC')).toBeInTheDocument()
  })
})
