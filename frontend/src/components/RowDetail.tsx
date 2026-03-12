import type { MediaItem } from '../api'

function formatDuration(secs: number | null): string {
  if (secs == null) return '-'
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = Math.floor(secs % 60)
  return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

function formatSize(bytes: number | null): string {
  if (bytes == null) return '-'
  return `${(bytes / 1e9).toFixed(2)} GB`
}

interface Props {
  item: MediaItem
}

export default function RowDetail({ item }: Props) {
  return (
    <div className="row-detail">
      <div className="row-detail-path">{item.path}</div>

      <div className="row-detail-meta">
        <span>Codec: {item.video_codec ?? '-'}</span>
        <span>Duration: {formatDuration(item.duration_secs)}</span>
        <span>Size: {formatSize(item.size_bytes)}</span>
        <span>HDR: {item.hdr ?? 'SDR'}</span>
        <span>FPS: {item.fps ?? '-'}</span>
        <span>Bitrate: {item.video_bitrate_kbps != null ? `${item.video_bitrate_kbps} kbps` : '-'}</span>
      </div>

      {item.audio_tracks.length > 0 && (
        <table className="tracks-table">
          <thead>
            <tr><th>Audio</th><th>Codec</th><th>Channels</th><th>Lang</th><th>Default</th></tr>
          </thead>
          <tbody>
            {item.audio_tracks.map(t => (
              <tr key={t.id}>
                <td>{t.track_index}</td>
                <td>{t.codec ?? '-'}</td>
                <td>{t.channels ?? '-'}</td>
                <td>{t.language ?? '-'}</td>
                <td>{t.is_default ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {item.subtitle_tracks.length > 0 && (
        <table className="tracks-table">
          <thead>
            <tr><th>Sub</th><th>Codec</th><th>Lang</th><th>Forced</th><th>Default</th></tr>
          </thead>
          <tbody>
            {item.subtitle_tracks.map(t => (
              <tr key={t.id}>
                <td>{t.track_index}</td>
                <td>{t.codec ?? '-'}</td>
                <td>{t.language ?? '-'}</td>
                <td>{t.forced ? 'Forced' : 'No'}</td>
                <td>{t.is_default ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
