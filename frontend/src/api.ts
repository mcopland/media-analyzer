const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface AudioTrack {
  id: number
  media_id: number
  track_index: number
  codec: string | null
  channels: number | null
  language: string | null
  is_default: boolean
}

export interface SubtitleTrack {
  id: number
  media_id: number
  track_index: number
  codec: string | null
  language: string | null
  forced: boolean
  is_default: boolean
}

export interface MediaItem {
  id: number
  filename: string
  path: string
  size_bytes: number | null
  mtime: number | null
  duration_secs: number | null
  width: number | null
  height: number | null
  fps: number | null
  video_codec: string | null
  video_bitrate_kbps: number | null
  overall_bitrate_kbps: number | null
  hdr: string | null
  container: string | null
  scanned_at: string
  audio_tracks: AudioTrack[]
  subtitle_tracks: SubtitleTrack[]
}

export interface MediaResponse {
  total: number
  items: MediaItem[]
}

export interface Filters {
  resolutions: string[]
  codecs: string[]
  hdr: string[]
  containers: string[]
  audio_langs: string[]
  sub_langs: string[]
}

export interface MediaParams {
  limit?: number
  offset?: number
  sortBy?: string
  sortDir?: string
  resolution?: string
  codec?: string
  hdr?: string
  container?: string
  audio_lang?: string
  sub_lang?: string
}

export async function fetchFilters(): Promise<Filters> {
  const resp = await fetch(`${BASE}/api/filters`)
  return resp.json()
}

export async function fetchMedia(params: MediaParams): Promise<MediaResponse> {
  const q = new URLSearchParams()
  if (params.limit != null) q.set('limit', String(params.limit))
  if (params.offset != null) q.set('offset', String(params.offset))
  if (params.sortBy) q.set('sort_by', params.sortBy)
  if (params.sortDir) q.set('sort_dir', params.sortDir)
  if (params.resolution) q.set('resolution', params.resolution)
  if (params.codec) q.set('codec', params.codec)
  if (params.hdr) q.set('hdr', params.hdr)
  if (params.container) q.set('container', params.container)
  if (params.audio_lang) q.set('audio_lang', params.audio_lang)
  if (params.sub_lang) q.set('sub_lang', params.sub_lang)
  const resp = await fetch(`${BASE}/api/media?${q}`)
  return resp.json()
}

export async function fetchMediaById(id: number): Promise<MediaItem> {
  const resp = await fetch(`${BASE}/api/media/${id}`)
  return resp.json()
}
