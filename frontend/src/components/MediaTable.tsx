import { Fragment, useState } from 'react'
import type { MediaItem } from '../api'
import RowDetail from './RowDetail'

const PAGE_SIZES = [10, 25, 50, 100]

interface Props {
  items: MediaItem[]
  total: number
  sortBy: string
  sortDir: string
  onSort: (col: string, dir: string) => void
  limit: number
  offset: number
  onPageChange: (limit: number, offset: number) => void
}

interface ColDef {
  key: string
  label: string
}

const COLUMNS: ColDef[] = [
  { key: 'filename', label: 'Filename' },
  { key: 'container', label: 'Container' },
  { key: 'video_codec', label: 'Codec' },
  { key: 'hdr', label: 'HDR' },
  { key: 'width', label: 'Width' },
  { key: 'height', label: 'Height' },
  { key: 'duration_secs', label: 'Duration' },
  { key: 'size_bytes', label: 'Size' },
]

function formatSize(bytes: number | null): string {
  if (bytes == null) return '-'
  return `${(bytes / 1e9).toFixed(1)} GB`
}

function formatDuration(secs: number | null): string {
  if (secs == null) return '-'
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  return h > 0 ? `${h}h ${m}m` : `${m}m`
}

function cellValue(item: MediaItem, key: string): string {
  const v = (item as unknown as Record<string, unknown>)[key]
  if (key === 'size_bytes') return formatSize(v as number | null)
  if (key === 'duration_secs') return formatDuration(v as number | null)
  return v != null ? String(v) : '-'
}

export default function MediaTable({ items, total, sortBy, sortDir, onSort, limit, offset, onPageChange }: Props) {
  const [expandedId, setExpandedId] = useState<number | null>(null)

  function handleHeaderClick(key: string) {
    if (key === sortBy) {
      onSort(key, sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      onSort(key, 'asc')
    }
  }

  function handleRowClick(id: number) {
    setExpandedId(prev => prev === id ? null : id)
  }

  const page = Math.floor(offset / limit)
  const totalPages = Math.ceil(total / limit)

  return (
    <div className="media-table-wrapper">
      <div className="table-controls">
        <span>{total} results</span>
        <label>
          Rows per page:{' '}
          <select value={limit} onChange={e => onPageChange(Number(e.target.value), 0)}>
            {PAGE_SIZES.map(s => <option key={s} value={s}>{s}</option>)}
            <option value={99999}>All</option>
          </select>
        </label>
      </div>

      <table className="media-table">
        <thead>
          <tr>
            {COLUMNS.map(col => (
              <th
                key={col.key}
                onClick={() => handleHeaderClick(col.key)}
                className={sortBy === col.key ? `sorted-${sortDir}` : ''}
                style={{ cursor: 'pointer' }}
              >
                {col.label}
                {sortBy === col.key ? (sortDir === 'asc' ? ' ^' : ' v') : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <Fragment key={item.id}>
              <tr onClick={() => handleRowClick(item.id)} style={{ cursor: 'pointer' }}>
                {COLUMNS.map(col => (
                  <td key={col.key}>{cellValue(item, col.key)}</td>
                ))}
              </tr>
              {expandedId === item.id && (
                <tr>
                  <td colSpan={COLUMNS.length}>
                    <RowDetail item={item} />
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button disabled={offset === 0} onClick={() => onPageChange(limit, Math.max(0, offset - limit))}>
          Prev
        </button>
        <span>Page {page + 1} of {totalPages || 1}</span>
        <button disabled={offset + limit >= total} onClick={() => onPageChange(limit, offset + limit)}>
          Next
        </button>
      </div>
    </div>
  )
}
