import type { Filters, MediaParams } from '../api'

interface Props {
  filters: Filters
  values: Partial<MediaParams>
  onChange: (next: Partial<MediaParams>) => void
}

interface SelectProps {
  label: string
  value: string
  options: string[]
  onChange: (v: string) => void
}

function FilterSelect({ label, value, options, onChange }: SelectProps) {
  return (
    <select value={value} onChange={e => onChange(e.target.value)}>
      <option value="">{label}</option>
      {options.map(o => (
        <option key={o} value={o}>{o}</option>
      ))}
    </select>
  )
}

export default function FilterBar({ filters, values, onChange }: Props) {
  const update = (key: keyof MediaParams) => (v: string) =>
    onChange({ ...values, [key]: v || undefined })

  return (
    <div className="filter-bar">
      <FilterSelect
        label="All resolutions"
        value={values.resolution ?? ''}
        options={filters.resolutions}
        onChange={update('resolution')}
      />
      <FilterSelect
        label="All codecs"
        value={values.codec ?? ''}
        options={filters.codecs}
        onChange={update('codec')}
      />
      <FilterSelect
        label="All HDR"
        value={values.hdr ?? ''}
        options={filters.hdr}
        onChange={update('hdr')}
      />
      <FilterSelect
        label="All containers"
        value={values.container ?? ''}
        options={filters.containers}
        onChange={update('container')}
      />
      <FilterSelect
        label="All audio langs"
        value={values.audio_lang ?? ''}
        options={filters.audio_langs}
        onChange={update('audio_lang')}
      />
      <FilterSelect
        label="All sub langs"
        value={values.sub_lang ?? ''}
        options={filters.sub_langs}
        onChange={update('sub_lang')}
      />
    </div>
  )
}
