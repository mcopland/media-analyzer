import { useState } from 'react'
import type { MediaParams } from './api'
import FilterBar from './components/FilterBar'
import MediaTable from './components/MediaTable'
import { useFilters } from './hooks/useFilters'
import { useMedia } from './hooks/useMedia'

const DEFAULT_LIMIT = 10

export default function App() {
  const [filters, setFilters] = useState<Partial<MediaParams>>({})
  const [sortBy, setSortBy] = useState('filename')
  const [sortDir, setSortDir] = useState('asc')
  const [limit, setLimit] = useState(DEFAULT_LIMIT)
  const [offset, setOffset] = useState(0)

  const filterOptions = useFilters()
  const { items, total } = useMedia({ ...filters, sortBy, sortDir, limit, offset })

  function handleFilterChange(next: Partial<MediaParams>) {
    setFilters(next)
    setOffset(0)
  }

  function handleSort(col: string, dir: string) {
    setSortBy(col)
    setSortDir(dir)
    setOffset(0)
  }

  function handlePageChange(newLimit: number, newOffset: number) {
    setLimit(newLimit)
    setOffset(newOffset)
  }

  return (
    <div className="app">
      <h1>Media Analyzer</h1>
      <FilterBar filters={filterOptions} values={filters} onChange={handleFilterChange} />
      <MediaTable
        items={items}
        total={total}
        sortBy={sortBy}
        sortDir={sortDir}
        onSort={handleSort}
        limit={limit}
        offset={offset}
        onPageChange={handlePageChange}
      />
    </div>
  )
}
