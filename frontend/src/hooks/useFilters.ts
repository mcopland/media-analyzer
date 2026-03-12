import { useEffect, useState } from 'react'
import { fetchFilters, type Filters } from '../api'

const empty: Filters = { resolutions: [], codecs: [], hdr: [], containers: [], audio_langs: [], sub_langs: [] }

export function useFilters() {
  const [filters, setFilters] = useState<Filters>(empty)

  useEffect(() => {
    fetchFilters().then(setFilters).catch(console.error)
  }, [])

  return filters
}
