import { useEffect, useState } from 'react'
import { fetchMedia, type MediaItem, type MediaParams } from '../api'

export function useMedia(params: MediaParams) {
  const [items, setItems] = useState<MediaItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetchMedia(params)
      .then(data => {
        setItems(data.items)
        setTotal(data.total)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [
    params.limit,
    params.offset,
    params.sortBy,
    params.sortDir,
    params.resolution,
    params.codec,
    params.hdr,
    params.container,
    params.audio_lang,
    params.sub_lang,
  ])

  return { items, total, loading }
}
