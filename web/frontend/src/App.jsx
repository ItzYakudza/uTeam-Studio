import React, { useState, useEffect, useCallback, useRef } from 'react'

const API = '/api'

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: opts.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(typeof err.detail === 'string' ? err.detail : res.statusText)
  }
  return res.json()
}

const STATUS_LABEL = {
  draft: 'Черновик',
  scripted: 'Сценарий',
  voiced: 'Озвучка',
  ready: 'Готов к сборке',
  rendered: 'Собран',
  error: 'Ошибка',
}

function formatDuration(value) {
  const seconds = Number(value)
  if (!Number.isFinite(seconds) || seconds < 0) return '--:--'
  const total = Math.floor(seconds)
  const s = String(total % 60).padStart(2, '0')
  const m = Math.floor(total / 60)
  if (m >= 60) {
    return `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}:${s}`
  }
  return `${String(m).padStart(2, '0')}:${s}`
}

function Modal({ title, children, onClose, footer }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-h">{title}</div>
        <div className="modal-b">{children}</div>
        {footer && <div className="modal-f">{footer}</div>}
      </div>
    </div>
  )
}


const RENDER_STAGES = [
  { id: 'prepare', label: 'Подготовка' },
  { id: 'voice', label: 'Голос и тайминги' },
  { id: 'validate', label: 'Проверка сцен' },
  { id: 'audio', label: 'Музыка и SFX' },
  { id: 'mix', label: 'Сведение аудио' },
  { id: 'encode', label: 'Кодирование MP4' },
  { id: 'thumb', label: 'Превью-кадр' },
]

function stageFromLogs(logs = []) {
  let current = 'prepare'
  const done = new Set()
  for (const line of logs) {
    if (typeof line !== 'string' || !line.startsWith('STAGE:')) continue
    const body = line.slice(6)
    const id = body.split('|')[0]
    if (id && id !== 'queued') {
      done.add(current)
      current = id
    }
  }
  // also infer from plain logs
  for (const line of logs) {
    if (typeof line !== 'string') continue
    if (line.includes('thumb.jpg')) { done.add(current); current = 'thumb' }
    if (line.includes('Done') || line.includes('saved')) { done.add(current); done.add('thumb'); current = 'done' }
  }
  return { current, done }
}

function parseStages(job = {}) {
  const logs = Array.isArray(job.log) ? job.log : []
  const parsed = stageFromLogs(logs)
  const aliases = {
    prepare: 'prepare',
    voice: 'audio',
    validate: 'scenes',
    audio: 'compose',
    mix: 'compose',
    encode: 'encode',
    thumb: 'done',
    done: 'done',
  }
  const current = aliases[parsed.current] || (job.status === 'done' ? 'done' : 'prepare')
  const done = Array.from(parsed.done || []).map((stage) => aliases[stage] || stage)
  if (job.status === 'done') done.push('done')
  return { current, done: [...new Set(done)] }
}

function jobProgress(job = {}) {
  if (job.status === 'done') return 100
  if (job.status === 'error' || job.status === 'cancelled' || job.status === 'queued') return 0
  const explicit = Number(job.progress)
  if (Number.isFinite(explicit) && explicit > 0) return Math.max(0, Math.min(99, explicit))
  const stages = parseStages(job)
  const order = ['prepare', 'audio', 'scenes', 'compose', 'encode', 'done']
  const index = Math.max(0, order.indexOf(stages.current))
  return Math.min(95, Math.round((index / (order.length - 1)) * 100))
}

function RenderTheater({ job, episodeTitle, mode, onMode, onClose, onCancel }) {
  if (!job) return null
  const progress = jobProgress(job)
  const stages = parseStages(job)
  const stageList = [
    { id: 'prepare', label: 'Подготовка' },
    { id: 'audio', label: 'Аудио' },
    { id: 'scenes', label: 'Сцены' },
    { id: 'compose', label: 'Сборка' },
    { id: 'encode', label: 'Кодирование' },
    { id: 'done', label: 'Готово' },
  ]
  const current = stages.current
  const done = new Set(stages.done || [])
  const isDone = job.status === 'done'
  const isErr = job.status === 'error' || job.status === 'cancelled'
  const statusLabel = isDone
    ? 'Рендер завершён'
    : job.status === 'cancelled'
      ? 'Отменено'
      : job.status === 'error'
        ? 'Ошибка'
        : job.status === 'queued'
          ? 'В очереди…'
          : 'Идёт рендер…'

  const plainLogs = (Array.isArray(job.log) ? job.log : [])
    .filter((l) => typeof l === 'string' && !String(l).startsWith('STAGE:'))
    .slice(-12)

  if (mode === 'mini') {
    return (
      <div className="render-mini" onClick={() => onMode && onMode('full')}>
        <div className="render-mini-bar"><i style={{ width: progress + '%' }} /></div>
        <div className="render-mini-body">
          <div style={{ minWidth: 0 }}>
            <div style={{ fontWeight: 600, fontSize: 13, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {episodeTitle || 'Рендер'}
            </div>
            <div className="muted">{statusLabel} · {Math.round(progress)}%</div>
          </div>
          <div className="row" onClick={(e) => e.stopPropagation()}>
            {!isDone && !isErr && (
              <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); onCancel && onCancel() }}>Отменить</button>
            )}
            <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); onMode && onMode('full') }}>На весь экран</button>
            <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); onClose && onClose() }}>Скрыть</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="render-theater render-theater-full">
      <div className="render-card render-card-full" onClick={(e) => e.stopPropagation()}>
        <div className={`render-hero render-hero-full ${isDone ? 'done' : ''} ${isErr ? 'err' : ''}`}>
          <div className="render-hero-inner">
            <div className="render-ring">{isDone ? '✓' : job.status === 'cancelled' ? '✕' : ''}</div>
            <div style={{ fontWeight: 700, fontSize: 18 }}>{statusLabel}</div>
            <div className="muted" style={{ marginTop: 6 }}>{Math.round(progress)}%</div>
          </div>
          {!isDone && !isErr && <div className="film-strip" />}
        </div>
        <div className="render-body render-body-full">
          <div className="render-title">{episodeTitle || 'Рендер'}</div>
          <div className="render-sub">
            {job.preview ? 'Быстрый превью' : 'Полный рендер'} · задача #{job.id}
            {job.channel_name ? ` · ${job.channel_name}` : ''}
          </div>
          <div className={`render-bar ${!isDone && !isErr && progress < 20 ? 'indeterminate' : ''}`}>
            <i style={{ width: progress + '%' }} />
          </div>
          <div className="render-stages render-stages-grid">
            {stageList.map((s) => {
              const stCls = isDone || done.has(s.id) ? 'done' : current === s.id ? 'active' : ''
              return (
                <div key={s.id} className={`render-stage ${stCls}`}>
                  <span className="bullet">{stCls === 'done' ? '✓' : ''}</span>
                  {s.label}
                </div>
              )
            })}
          </div>
          {job.status === 'error' && job.error && (
            <div style={{ color: 'var(--red)', fontSize: 13, marginBottom: 8 }}>{job.error}</div>
          )}
          {plainLogs.length > 0 && (
            <div className="render-log render-log-full">
              {plainLogs.map((l, i) => (
                <div key={i}>{l}</div>
              ))}
            </div>
          )}
          <div className="render-actions">
            {!isDone && !isErr && (
              <>
                <button className="btn btn-danger" onClick={onCancel}>Отменить</button>
                <button className="btn btn-ghost" onClick={() => onMode && onMode('mini')}>Свернуть</button>
              </>
            )}
            <button className="btn btn-primary" onClick={onClose}>{isDone ? 'Готово' : isErr ? 'Закрыть' : 'Скрыть окно'}</button>
          </div>
        </div>
      </div>
    </div>
  )
}


export default function App()
 {
  const [page, setPage] = useState('content') // content | episode | channels | renders | analytics | system
  const [channels, setChannels] = useState([])
  const [episodes, setEpisodes] = useState([])
  const [channelFilter, setChannelFilter] = useState(null)
  const [kindFilter, setKindFilter] = useState(null)
  const [statusFilter, setStatusFilter] = useState(null)
  const [q, setQ] = useState('')
  const [selected, setSelected] = useState(null)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [toast, setToast] = useState(null)
  const [preview, setPreview] = useState(false)

  const [showNewChannel, setShowNewChannel] = useState(false)
  const [showNewEpisode, setShowNewEpisode] = useState(false)
  const [newChannelName, setNewChannelName] = useState('')
  const [newEpTitle, setNewEpTitle] = useState('')
  const [newEpKind, setNewEpKind] = useState('shorts')
  const [newEpChannel, setNewEpChannel] = useState(null)

  const [tab, setTab] = useState('script')
  const [script, setScript] = useState('')
  const [scenes, setScenes] = useState('')
  const [dirty, setDirty] = useState(false)
  const [saving, setSaving] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [doctor, setDoctor] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [analyticsVideo, setAnalyticsVideo] = useState(null)
  const [analyticsTab, setAnalyticsTab] = useState('overview') // overview | formats | ranking
  const [lastSyncAt, setLastSyncAt] = useState(null)
  const [syncNowBusy, setSyncNowBusy] = useState(false)
  const [channelYtUrl, setChannelYtUrl] = useState('')
  const [oauthStatus, setOauthStatus] = useState(null)
  const [activeJobId, setActiveJobId] = useState(null)
  const [renderTitle, setRenderTitle] = useState('')
  const [showTheater, setShowTheater] = useState(false)
  const [theaterMode, setTheaterMode] = useState('full') // full | mini
  const [ytUrl, setYtUrl] = useState('')
  const [ytBusy, setYtBusy] = useState(false)
  const [statsForm, setStatsForm] = useState({ episode_id: '', date: new Date().toISOString().slice(0, 10), views: 0, likes: 0, comments: 0, watch_time_h: 0 })
  const fileRef = useRef(null)

  const notify = (msg, err = false) => {
    setToast({ msg, err })
    setTimeout(() => setToast(null), 2800)
  }

  const loadChannels = useCallback(async () => {
    try {
      const data = await api('/channels')
      setChannels(data)
      if (!newEpChannel && data.length) setNewEpChannel(data[0].id)
    } catch (e) {
      setError(e.message)
    }
  }, [newEpChannel])

  const loadEpisodes = useCallback(async () => {
    try {
      setError(null)
      const params = new URLSearchParams()
      if (channelFilter) params.set('channel_id', channelFilter)
      if (kindFilter) params.set('kind', kindFilter)
      if (statusFilter) params.set('status', statusFilter)
      if (q.trim()) params.set('q', q.trim())
      const data = await api('/episodes?' + params.toString())
      setEpisodes(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [channelFilter, kindFilter, statusFilter, q])

  const loadJobs = useCallback(async () => {
    try {
      setJobs(await api('/jobs'))
    } catch {}
  }, [])

  useEffect(() => {
    loadChannels()
    loadEpisodes()
    loadJobs()
    loadOauthStatus()
  }, [loadChannels, loadEpisodes, loadJobs])

  // Quietly refresh the sync timestamp and the currently visible dashboard every minute.
  useEffect(() => {
    let cancelled = false
    const tick = async () => {
      try {
        const state = await api('/sync-status')
        if (!cancelled) setLastSyncAt(state.last_sync_at || null)
      } catch {}
      if (page === 'analytics') {
        try {
          const data = await api('/analytics/dashboard')
          if (!cancelled) setAnalytics(data)
        } catch {}
      } else if (page === 'content') {
        try { await loadEpisodes() } catch {}
      }
    }
    tick()
    const timer = setInterval(tick, 60 * 1000)
    return () => { cancelled = true; clearInterval(timer) }
  }, [page, loadEpisodes])

  async function syncNow() {
    if (syncNowBusy) return
    setSyncNowBusy(true)
    try {
      const result = await api('/sync-now', { method: 'POST' })
      const state = result.sync || await api('/sync-status')
      setLastSyncAt(state.last_sync_at || null)
      if (page === 'analytics') setAnalytics(await api('/analytics/dashboard'))
      if (page === 'content') await loadEpisodes()
      notify('Статистика обновлена')
    } catch (e) {
      notify(e.message || 'Не удалось обновить статистику', true)
    } finally {
      setSyncNowBusy(false)
    }
  }

  // Renders tab: jobs a bit more often
  useEffect(() => {
    if (page !== 'renders') return
    const t = setInterval(() => loadJobs(), 15 * 1000)
    return () => clearInterval(t)
  }, [page, loadJobs])

  // While render theater is open — poll job status frequently
  useEffect(() => {
    if (!showTheater || !activeJobId) return
    loadJobs()
    const t = setInterval(() => loadJobs(), 2000)
    return () => clearInterval(t)
  }, [showTheater, activeJobId, loadJobs])

  async function openEpisode(ep) {
    setSelected(ep)
    setPage('episode')
    setDirty(false)
    setTab('script')
    try {
      const [s, sc] = await Promise.all([
        api(`/episodes/${ep.id}/file?name=script.txt`),
        api(`/episodes/${ep.id}/file?name=scenes.py`),
      ])
      setScript(s.content || '')
      setScenes(sc.content || '')
      const fresh = await api(`/episodes/${ep.id}`)
      setSelected(fresh)
      setYtUrl(fresh.youtube_url || fresh.youtube_id || '')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function saveFiles() {
    if (!selected) return
    setSaving(true)
    try {
      await Promise.all([
        api(`/episodes/${selected.id}/file?name=script.txt`, {
          method: 'PUT',
          body: JSON.stringify({ content: script }),
        }),
        api(`/episodes/${selected.id}/file?name=scenes.py`, {
          method: 'PUT',
          body: JSON.stringify({ content: scenes }),
        }),
      ])
      setDirty(false)
      const fresh = await api(`/episodes/${selected.id}`)
      setSelected(fresh)
      notify('Сохранено')
      loadEpisodes()
    } catch (e) {
      notify(e.message, true)
    } finally {
      setSaving(false)
    }
  }

  async function createChannel() {
    if (!newChannelName.trim()) return
    try {
      await api('/channels', { method: 'POST', body: JSON.stringify({ name: newChannelName }) })
      setShowNewChannel(false)
      setNewChannelName('')
      await loadChannels()
      notify('Канал создан')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function createEpisode() {
    if (!newEpTitle.trim() || !newEpChannel) return
    try {
      const ep = await api('/episodes', {
        method: 'POST',
        body: JSON.stringify({ channel_id: newEpChannel, title: newEpTitle, kind: newEpKind }),
      })
      setShowNewEpisode(false)
      setNewEpTitle('')
      await loadEpisodes()
      notify('Видео создано')
      openEpisode(ep)
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function removeEpisode(ep) {
    if (!confirm(`Удалить «${ep.title}»?`)) return
    try {
      await api(`/episodes/${ep.id}`, { method: 'DELETE' })
      if (selected?.id === ep.id) {
        setSelected(null)
        setPage('content')
      }
      await loadEpisodes()
      notify('Удалено')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function startRender(ep) {
    try {
      const res = await api('/render', {
        method: 'POST',
        body: JSON.stringify({ episode_id: ep.id, preview }),
      })
      setRenderTitle(ep.title || 'Рендер')
      setActiveJobId(res.job_id)
      setTheaterMode('full')
      setShowTheater(true)
      notify(preview ? 'Быстрый превью запущен' : 'Полный рендер запущен')
      loadJobs()
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function startSheet(ep) {
    try {
      await api('/sheet', { method: 'POST', body: JSON.stringify({ episode_id: ep.id }) })
      notify('Сетка кадров запущена')
      loadJobs()
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function uploadVoice(file) {
    if (!selected || !file) return
    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${API}/episodes/${selected.id}/voice`, { method: 'POST', body: fd })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || res.statusText)
      }
      const fresh = await res.json()
      setSelected(fresh)
      notify('Озвучка загружена')
      loadEpisodes()
    } catch (e) {
      notify(e.message, true)
    } finally {
      setUploading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  async function runDoctor() {
    try {
      setDoctor(await api('/doctor'))
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function linkYoutube(ep, updateTitle = false) {
    if (!ytUrl.trim()) return notify('Вставь ссылку на YouTube', true)
    setYtBusy(true)
    try {
      const res = await api(`/episodes/${ep.id}/youtube`, {
        method: 'POST',
        body: JSON.stringify({ url: ytUrl.trim(), sync_stats: true, update_title: updateTitle }),
      })
      setSelected(res.episode)
      setYtUrl(res.episode.youtube_url || ytUrl)
      notify(`YouTube OK · ${res.youtube?.views ?? 0} views`)
      loadEpisodes()
      if (page === 'analytics') setAnalytics(await api('/analytics/dashboard'))
    } catch (e) {
      notify(e.message, true)
    } finally {
      setYtBusy(false)
    }
  }

  async function syncYoutube(ep) {
    setYtBusy(true)
    try {
      const res = await api(`/episodes/${ep.id}/youtube/sync`, { method: 'POST' })
      setSelected(res.episode)
      notify(`Обновлено · ${res.youtube?.views ?? 0} просмотров`)
      loadEpisodes()
      if (page === 'analytics') setAnalytics(await api('/analytics/dashboard'))
    } catch (e) {
      notify(e.message, true)
    } finally {
      setYtBusy(false)
    }
  }

  
  async function loadOauthStatus() {
    try {
      setOauthStatus(await api('/oauth/youtube/status'))
    } catch (e) {
      setOauthStatus({ connected: false, error: e.message })
    }
  }

  async function connectYoutubeOauth() {
    try {
      const r = await api('/oauth/youtube/start')
      window.open(r.auth_url, 'yt_oauth', 'width=520,height=720')
      notify('Открой окно Google и разреши доступ')
      // poll status
      let n = 0
      const timer = setInterval(async () => {
        n += 1
        await loadOauthStatus()
        const s = await api('/oauth/youtube/status')
        setOauthStatus(s)
        if (s.connected || n > 60) clearInterval(timer)
      }, 2000)
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function disconnectYoutubeOauth() {
    try {
      await api('/oauth/youtube/disconnect', { method: 'POST' })
      setOauthStatus(await api('/oauth/youtube/status'))
      notify('YouTube отключён')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function openAnalyticsVideo(epId) {
    try {
      const data = await api(`/episodes/${epId}/analytics`)
      setAnalyticsVideo(data)
      setPage('analytics')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function toggleAggregate(epId, include) {
    try {
      await api(`/episodes/${epId}/aggregate`, {
        method: 'POST',
        body: JSON.stringify({ include }),
      })
      setAnalytics(await api('/analytics/dashboard'))
      if (analyticsVideo?.episode?.id === epId) {
        const data = await api(`/episodes/${epId}/analytics`)
        setAnalyticsVideo(data)
      }
      notify(include ? 'В общей статистике' : 'Исключено из общей')
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function saveChannelYt(channelId) {
    try {
      await api(`/channels/${channelId}`, {
        method: 'PATCH',
        body: JSON.stringify({ youtube_channel_url: channelYtUrl }),
      })
      notify('Канал YouTube сохранён')
      loadChannels()
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function autoLinkChannel(channelId) {
    setYtBusy(true)
    try {
      const res = await api(`/channels/${channelId}/youtube/auto-link`, { method: 'POST' })
      notify(`Автопривязка: ${(res.linked || []).length} из ${res.candidates}`)
      loadEpisodes()
      try { setAnalytics(await api('/analytics/dashboard')) } catch {}
    } catch (e) {
      notify(e.message, true)
    } finally {
      setYtBusy(false)
    }
  }

  async function deleteJob(id) {
    try {
      await api(`/jobs/${id}`, { method: 'DELETE' })
      notify('Запись удалена')
      loadJobs()
    } catch (e) { notify(e.message, true) }
  }

  async function cancelJob(jobId) {
    try {
      await api(`/jobs/${jobId}/cancel`, { method: 'POST' })
      notify('Рендер отменяется…')
      loadJobs()
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function syncAllYoutube() {
    setYtBusy(true)
    try {
      const res = await api('/youtube/sync-all', { method: 'POST' })
      notify(`Обновлено: ${res.synced} ок, ${res.skipped} без ссылки, ${res.failed} ошибок`)
      loadEpisodes()
      setAnalytics(await api('/analytics/dashboard'))
    } catch (e) {
      notify(e.message, true)
    } finally {
      setYtBusy(false)
    }
  }

  async function runMigrate() {
    try {
      const r = await api('/migrate', { method: 'POST' })
      notify(`Импорт: каналов ${r.channels}, эпизодов ${r.episodes}`)
      await loadChannels()
      await loadEpisodes()
    } catch (e) {
      notify(e.message, true)
    }
  }

  const stats = {
    total: episodes.length,
    ready: episodes.filter((e) => e.status === 'ready').length,
    rendered: episodes.filter((e) => e.status === 'rendered').length,
    voiced: episodes.filter((e) => e.has_voice).length,
  }

  const recentJobs = jobs.slice(0, 5)

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">uT</div>
          <div>
            <div className="brand-text">uTeam Studio</div>
            <div className="brand-sub">Creator dashboard</div>
          </div>
        </div>

        <div
          className={`nav-item ${page === 'content' ? 'active' : ''}`}
          onClick={() => {
            setPage('content')
            setSelected(null)
          }}
        >
          <span className="dot" /> Контент
        </div>
        <div
          className={`nav-item ${page === 'channels' ? 'active' : ''}`}
          onClick={() => setPage('channels')}
        >
          <span className="dot" /> Каналы
        </div>
        <div
          className={`nav-item ${page === 'renders' ? 'active' : ''}`}
          onClick={() => setPage('renders')}
        >
          <span className="dot" /> Рендеры
          {jobs.filter((j) => j.status === 'running' || j.status === 'queued').length > 0 && (
            <span style={{ marginLeft: 'auto', background: 'var(--accent)', color: '#000', borderRadius: 99, padding: '1px 7px', fontSize: 11 }}>
              {jobs.filter((j) => j.status === 'running' || j.status === 'queued').length}
            </span>
          )}
        </div>
        <div className="section-label">Данные</div>
        <div
          className={`nav-item ${page === 'analytics' ? 'active' : ''}`}
          onClick={async () => {
            setPage('analytics')
            try { setAnalytics(await api('/analytics/dashboard')) } catch (e) { notify(e.message, true) }
          }}
        >
          <span className="dot" /> Аналитика
        </div>
        <div
          className={`nav-item ${page === 'system' ? 'active' : ''}`}
          onClick={() => {
            setPage('system')
            runDoctor()
            loadOauthStatus()
          }}
        >
          <span className="dot" /> Система
        </div>

        <div className="section-label">Фильтр канала</div>
        <div
          className={`nav-item ${channelFilter === null && page === 'content' ? 'active' : ''}`}
          onClick={() => {
            setChannelFilter(null)
            setPage('content')
          }}
        >
          Все
        </div>
        {channels.map((c) => (
          <div
            key={c.id}
            className={`nav-item ${channelFilter === c.id ? 'active' : ''}`}
            onClick={() => {
              setChannelFilter(c.id)
              setPage('content')
            }}
          >
            {c.name}
            <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-3)' }}>
              {c.episodes_count || 0}
            </span>
          </div>
        ))}

        <div style={{ marginTop: 'auto', padding: '16px 8px 0', display: 'flex', flexDirection: 'column', gap: 8 }}>
          <button className="btn btn-primary" onClick={() => { setNewEpChannel(channels[0]?.id ?? null); setShowNewEpisode(true) }}>
            + Новое видео
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowNewChannel(true)}>
            + Канал
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          {(page === 'content') ? (
            <input
              className="search"
              placeholder="Поиск по названию, тегам…"
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          ) : (
            <div className="muted" style={{ fontSize: 13 }}>
              {page === 'episode' && 'Редактор ролика'}
              {page === 'channels' && 'Каналы'}
              {page === 'renders' && 'Очередь и история рендеров'}
              {page === 'analytics' && 'Аналитика канала'}
              {page === 'system' && 'Настройки и окружение'}
            </div>
          )}
          <div className="row">
            <span className="muted" style={{ fontSize: 11, whiteSpace: 'nowrap', padding: '5px 9px', border: '1px solid var(--border)', borderRadius: 999, background: 'var(--panel)' }} title={lastSyncAt || 'Синхронизация ещё не выполнялась'}>
              Последнее обновление: {lastSyncAt ? new Date(lastSyncAt).toLocaleTimeString('ru-RU', { hour12: false }) : '—'}
            </span>
            <button className="btn btn-primary btn-sm" onClick={syncNow} disabled={syncNowBusy}>
              {syncNowBusy ? 'Обновление…' : 'Обновить сейчас'}
            </button>
            {page === 'content' && (
              <label className="muted" style={{ display: 'flex', alignItems: 'center', gap: 6 }} title="Низкое качество, быстрее проверить сборку">
                <input type="checkbox" checked={preview} onChange={(e) => setPreview(e.target.checked)} /> Быстрый превью
              </label>
            )}
            {page === 'content' && (
              <button className="btn btn-ghost btn-sm" onClick={() => { loadEpisodes(); loadChannels() }}>
                Обновить список
              </button>
            )}
            {page === 'renders' && (
              <button className="btn btn-ghost btn-sm" onClick={loadJobs}>Обновить очередь</button>
            )}
            {page === 'analytics' && (
              <button className="btn btn-ghost btn-sm" onClick={async () => {
                try { setAnalytics(await api('/analytics/dashboard')) } catch (e) { notify(e.message, true) }
              }}>Обновить обзор</button>
            )}
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="panel" style={{ marginBottom: 16, borderColor: 'var(--red)' }}>
              <div className="panel-b" style={{ color: 'var(--red)' }}>
                API: {error}. Запусти backend на :5050
              </div>
            </div>
          )}

          {page === 'content' && (
            <>
              <div className="page-title">Контент канала</div>
              <div className="page-sub">
                {oauthStatus?.connected
                  ? 'OAuth подключён — статистика и метаданные с YouTube подтягиваются автоматически'
                  : 'Как YouTube Studio — список роликов, статусы, быстрые действия. Подключи OAuth в «Система» для авто-обновления.'}
              </div>

              <div className="stats">
                <div className="stat"><div className="stat-val">{stats.total}</div><div className="stat-label">Всего</div></div>
                <div className="stat"><div className="stat-val">{stats.voiced}</div><div className="stat-label">С озвучкой</div></div>
                <div className="stat"><div className="stat-val">{stats.ready}</div><div className="stat-label">К сборке</div></div>
                <div className="stat"><div className="stat-val">{stats.rendered}</div><div className="stat-label">Собрано</div></div>
              </div>

              <div className="filters">
                <button className={`chip ${!kindFilter ? 'active' : ''}`} onClick={() => setKindFilter(null)}>Все типы</button>
                <button className={`chip ${kindFilter === 'shorts' ? 'active' : ''}`} onClick={() => setKindFilter('shorts')}>Shorts</button>
                <button className={`chip ${kindFilter === 'long' ? 'active' : ''}`} onClick={() => setKindFilter('long')}>Long</button>
                <span className="muted">|</span>
                <button className={`chip ${!statusFilter ? 'active' : ''}`} onClick={() => setStatusFilter(null)}>Любой статус</button>
                {['ready', 'rendered', 'voiced', 'scripted', 'error'].map((s) => (
                  <button key={s} className={`chip ${statusFilter === s ? 'active' : ''}`} onClick={() => setStatusFilter(s)}>
                    {STATUS_LABEL[s] || s}
                  </button>
                ))}
              </div>

              {loading ? (
                <div className="empty">Загрузка…</div>
              ) : episodes.length === 0 ? (
                <div className="empty">
                  <h3>Пока нет видео</h3>
                  <p style={{ marginBottom: 16 }}>Создай ролик или импортируй старые папки</p>
                  <div className="row" style={{ justifyContent: 'center' }}>
                    <button className="btn btn-primary" onClick={() => setShowNewEpisode(true)}>+ Новое видео</button>
                    <button className="btn btn-ghost" onClick={runMigrate}>Импорт из папок</button>
                  </div>
                </div>
              ) : (
                <div className="video-grid">
                  {episodes.map((ep) => (
                    <div
                      key={ep.id}
                      className={`video-card ${selected?.id === ep.id ? 'selected' : ''}`}
                      onClick={() => openEpisode(ep)}
                    >
                      <div className={`thumb ${ep.kind === 'shorts' ? 'shorts' : ''}`} style={ep.has_preview || ep.has_thumb ? { backgroundImage: `url(${API}/episodes/${ep.id}/thumb?t=${ep.updated_at||''})`, backgroundSize: 'cover', backgroundPosition: 'center' } : undefined}>
                        <span className={`status-pill status-${ep.status}`}>
                          {STATUS_LABEL[ep.status] || ep.status}
                        </span>
                        {!(ep.has_preview || ep.has_thumb) && <span>{ep.kind === 'shorts' ? 'Shorts' : 'Video'}</span>}
                        {ep.has_video && <span className="thumb-badge">{formatDuration(ep.duration_sec)}</span>}
                      </div>
                      <div className="video-body">
                        <div className="video-title">{ep.title}</div>
                        <div className="video-meta">
                          <span>{ep.channel_name}</span>
                          <span>·</span>
                          <span>{ep.kind === 'shorts' ? 'Shorts' : 'Long'}</span>
                          <span>·</span>
                          <span>{ep.has_voice ? 'Озвучка есть' : 'Нет озвучки'}</span>
                          {ep.yt_views != null && <span>· {Number(ep.yt_views).toLocaleString('ru-RU')} просм.</span>}
                        </div>
                        <div className="video-actions" onClick={(e) => e.stopPropagation()}>
                          <button className="btn btn-sm btn-primary" onClick={() => openEpisode(ep)}>Открыть</button>
                          <button className="btn btn-sm btn-ghost" onClick={() => openAnalyticsVideo(ep.id)}>Метрики</button>
                          <button className="btn btn-sm btn-danger" onClick={() => removeEpisode(ep)}>Удалить</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

          {page === 'episode' && selected && (
            <>
              <div className="row" style={{ marginBottom: 12 }}>
                <button className="btn btn-ghost btn-sm" onClick={() => setPage('content')}>← Назад</button>
                <div>
                  <div className="page-title" style={{ marginBottom: 0 }}>{selected.title}</div>
                  <div className="muted">
                    {selected.channel_name} · {selected.kind} · {STATUS_LABEL[selected.status]}
                  </div>
                </div>
                <div style={{ marginLeft: 'auto' }} className="row">
                  <button className="btn btn-ghost btn-sm" onClick={saveFiles} disabled={!dirty || saving}>
                    {saving ? '…' : 'Сохранить'}
                  </button>
                  <button
                    className="btn btn-success btn-sm"
                    disabled={!selected.has_voice || !selected.has_scenes}
                    onClick={() => startRender(selected)}
                  >
                    {preview ? 'Быстрый превью' : 'Собрать ролик'}
                  </button>
                </div>
              </div>

              <div className="detail">
                <div className="panel">
                  <div className="tabs">
                    <button className={`tab ${tab === 'script' ? 'active' : ''}`} onClick={() => setTab('script')}>Сценарий</button>
                    <button className={`tab ${tab === 'scenes' ? 'active' : ''}`} onClick={() => setTab('scenes')}>scenes.py</button>
                  </div>
                  <textarea
                    className="editor"
                    value={tab === 'script' ? script : scenes}
                    onChange={(e) => {
                      setDirty(true)
                      if (tab === 'script') setScript(e.target.value)
                      else setScenes(e.target.value)
                    }}
                    spellCheck={false}
                  />
                </div>

                <div>
                  <div className="panel" style={{ marginBottom: 16 }}>
                    <div className="panel-h">Чеклист</div>
                    <div className="panel-b">
                      <ul className="checklist">
                        <li><span className={`check ${selected.has_script ? 'on' : ''}`}>{selected.has_script ? '✓' : ''}</span> script.txt</li>
                        <li><span className={`check ${selected.has_scenes ? 'on' : ''}`}>{selected.has_scenes ? '✓' : ''}</span> scenes.py</li>
                        <li><span className={`check ${selected.has_voice ? 'on' : ''}`}>{selected.has_voice ? '✓' : ''}</span> voiceover.mp3</li>
                        <li><span className={`check ${selected.has_video ? 'on' : ''}`}>{selected.has_video ? '✓' : ''}</span> Готовое видео</li>
                        <li><span className={`check ${selected.has_meta ? 'on' : ''}`}>{selected.has_meta ? '✓' : ''}</span> Metadata</li>
                      </ul>
                    </div>
                  </div>

                  <div className="panel" style={{ marginBottom: 16 }}>
                    <div className="panel-h">YouTube</div>
                    <div className="panel-b">
                      {selected.youtube_id ? (
                        <div className="muted" style={{ marginBottom: 8 }}>
                          Привязано:{' '}
                          <a href={selected.youtube_url || `https://youtu.be/${selected.youtube_id}`} target="_blank" rel="noreferrer">
                            {selected.youtube_id}
                          </a>
                        </div>
                      ) : (
                        <div className="muted" style={{ marginBottom: 8 }}>Ссылка ещё не привязана</div>
                      )}
                      <div className="field">
                        <label>Ссылка или ID</label>
                        <input
                          value={ytUrl}
                          onChange={(e) => setYtUrl(e.target.value)}
                          placeholder="https://youtube.com/watch?v=... или shorts/..."
                        />
                      </div>
                      <p className="muted" style={{ marginBottom: 8 }}>
                        Данные пишутся в папку ролика <code>youtube_data/</code> (meta, stats, thumb). Воркер обновляет раз в час.
                      </p>
                      <div className="row">
                        <button className="btn btn-primary btn-sm" disabled={ytBusy} onClick={() => linkYoutube(selected, false)} title="Привязать ссылку и скачать метрики">
                          {ytBusy ? '…' : 'Привязать + статистика'}
                        </button>
                        <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={() => linkYoutube(selected, true)}>
                          + обновить title
                        </button>
                        {selected.youtube_id && (
                          <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={() => syncYoutube(selected)}>
                            Обновить с YouTube
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="panel">
                    <div className="panel-h">Действия</div>
                    <div className="panel-b" style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      <button className="btn btn-ghost" onClick={() => fileRef.current?.click()} disabled={uploading}>
                        {uploading ? 'Загрузка…' : 'Загрузить озвучку'}
                      </button>
                      <button className="btn btn-success" disabled={!selected.has_voice || !selected.has_scenes} onClick={() => startRender(selected)}>
                        Собрать ролик{preview ? ' (быстрый)' : ''}
                      </button>
                      <button className="btn btn-ghost" disabled={!selected.has_voice} onClick={() => startSheet(selected)}>
                        Контактный лист
                      </button>
                      {selected.has_video && (
                        <a className="btn btn-primary" href={`${API}/download?episode_id=${selected.id}&kind=video`} target="_blank" rel="noreferrer">
                          Скачать MP4
                        </a>
                      )}
                      {selected.has_meta && (
                        <a className="btn btn-ghost" href={`${API}/download?episode_id=${selected.id}&kind=meta`} target="_blank" rel="noreferrer">
                          Метаданные
                        </a>
                      )}
                      <button className="btn btn-danger btn-sm" onClick={() => removeEpisode(selected)}>
                        Удалить видео
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}

          {page === 'channels' && (
            <>
              <div className="page-title">Каналы</div>
              <div className="page-sub">Управление каналами. Данные в SQLite, файлы в storage/</div>
              <div className="row" style={{ marginBottom: 16 }}>
                <button className="btn btn-primary" onClick={() => setShowNewChannel(true)}>+ Канал</button>
                <button className="btn btn-ghost" onClick={runMigrate} title="Перенести эпизоды из старой структуры папок в storage">Импорт из папок</button>
              </div>
              <div className="video-grid">
                {channels.map((c) => (
                  <div key={c.id} className="video-card" style={{ cursor: 'default' }}>
                    <div className="video-body">
                      <div className="video-title" style={{ cursor: 'pointer' }} onClick={() => { setChannelFilter(c.id); setPage('content') }}>{c.name}</div>
                      <div className="video-meta">
                        {c.shorts_count || 0} shorts · {c.longs_count || 0} long
                      </div>
                      <div className="field" style={{ marginTop: 10 }} onClick={(e) => e.stopPropagation()}>
                        <label>YouTube канал (URL или @handle)</label>
                        <input
                          defaultValue={c.youtube_channel_url || ''}
                          placeholder="https://youtube.com/@channel/videos"
                          onFocus={() => setChannelYtUrl(c.youtube_channel_url || '')}
                          onChange={(e) => setChannelYtUrl(e.target.value)}
                        />
                      </div>
                      <div className="video-actions" onClick={(e) => e.stopPropagation()}>
                        <button className="btn btn-sm btn-primary" onClick={() => saveChannelYt(c.id)}>Сохранить URL</button>
                        <button className="btn btn-sm btn-ghost" disabled={ytBusy} onClick={() => autoLinkChannel(c.id)}>Автопривязка видео</button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={async () => {
                            if (!confirm(`Удалить канал ${c.name}?`)) return
                            await api(`/channels/${c.id}`, { method: 'DELETE' })
                            loadChannels()
                            loadEpisodes()
                          }}
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}


          
          {page === 'renders' && (
            <>
              <div className="an-head" style={{ marginBottom: 8 }}>
                <div>
                  <div className="page-title">Рендеры</div>
                  <div className="page-sub" style={{ marginBottom: 0 }}>Очередь и история сборок. Активные задачи сверху.</div>
                </div>
                <div className="an-actions">
                  <button className="btn btn-ghost btn-sm" onClick={loadJobs}>Обновить список</button>
                  <button className="btn btn-danger btn-sm" onClick={async () => {
                    if (!confirm('Удалить всю историю завершённых рендеров? Активные задачи останутся.')) return
                    try {
                      const r = await api('/jobs/clear-history?only_finished=true', { method: 'POST' })
                      notify(`Удалено записей: ${r.removed || 0}`)
                      loadJobs()
                    } catch (e) { notify(e.message, true) }
                  }}>Очистить историю</button>
                </div>
              </div>

              <div className="video-grid">
                {jobs.length === 0 ? (
                  <div className="empty">Пока нет задач рендера</div>
                ) : (
                  jobs.slice(0, 20).map((j) => {
                    const active = j.status === 'running' || j.status === 'queued'
                    return (
                      <div key={j.id} className="video-card" style={{ cursor: 'default' }}>
                        <div className="video-body">
                          <div className="video-title">{j.episode_title || `Job #${j.id}`}</div>
                          <div className="video-meta">
                            <span className={active ? 'job-run' : j.status === 'done' ? 'job-ok' : 'job-err'}>
                              {j.status === 'done' ? 'Готово' : j.status === 'running' ? 'Идёт' : j.status === 'queued' ? 'Очередь' : j.status === 'cancelled' ? 'Отменено' : j.status === 'error' ? 'Ошибка' : j.status}
                            </span>
                            <span>·</span>
                            <span>{j.kind}</span>
                            {j.preview ? <span>· быстрый</span> : null}
                          </div>
                          <div className="video-actions">
                            {active && (
                              <>
                                <button className="btn btn-sm btn-primary" onClick={() => {
                                  setActiveJobId(j.id)
                                  setRenderTitle(j.episode_title || `Job #${j.id}`)
                                  setTheaterMode('full')
                                  setShowTheater(true)
                                }}>На весь экран</button>
                                <button className="btn btn-sm btn-ghost" onClick={() => {
                                  setActiveJobId(j.id)
                                  setRenderTitle(j.episode_title || `Job #${j.id}`)
                                  setTheaterMode('mini')
                                  setShowTheater(true)
                                }}>Свернуть</button>
                                <button className="btn btn-sm btn-danger" onClick={() => cancelJob(j.id)}>Отменить</button>
                              </>
                            )}
                            {!active && (
                              <button className="btn btn-sm btn-ghost" onClick={() => {
                                setActiveJobId(j.id)
                                setRenderTitle(j.episode_title || `Job #${j.id}`)
                                setTheaterMode('full')
                                setShowTheater(true)
                              }}>Открыть</button>
                            )}
                            {!active && (
                              <button className="btn btn-sm btn-danger" onClick={() => deleteJob(j.id)}>Удалить</button>
                            )}
                          </div>
                        </div>
                      </div>
                    )
                  })
                )}
              </div>
            </>
          )}

          {page === 'analytics' && (
            <div className="an-wrap">
              <div className="an-head">
                <div className="an-head-left">
                  <div className="page-title" style={{ marginBottom: 4 }}>Аналитика</div>
                  <div className="page-sub" style={{ marginBottom: 0 }}>
                    {oauthStatus?.connected
                      ? 'Live YouTube · Data API сразу · Studio Metrics после 24ч'
                      : 'Подключи OAuth в «Система», чтобы подтянуть метрики канала'}
                  </div>
                </div>
                <div className="an-actions">
                  <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={async () => {
                    await syncAllYoutube()
                    try { setAnalytics(await api('/analytics/dashboard')) } catch {}
                  }}>{ytBusy ? 'Обновление…' : 'Обновить с YouTube'}</button>
                  <button className="btn btn-ghost btn-sm" onClick={async () => {
                    try { setAnalytics(await api('/analytics/dashboard')) } catch (e) { notify(e.message, true) }
                  }} title="Пересчитать обзор без полного синка">Обновить обзор</button>
                  <button className="btn btn-primary btn-sm" onClick={async () => {
                    try {
                      await navigator.clipboard.writeText(analytics?.ai_prompt_text || '')
                      notify('Сводка для ИИ скопирована')
                    } catch { notify('Не удалось скопировать', true) }
                  }} title="Скопировать структурированный промпт для ИИ-аналитика">Скопировать промпт для аналитика</button>
                  <a className="btn btn-ghost btn-sm" href={`${API}/analytics/export?format=json`} target="_blank" rel="noreferrer" title="Скачать сырые данные">Экспорт JSON</a>
                </div>
              </div>

              <div className="an-pills">
                <button className={`an-pill ${analyticsTab === 'overview' ? 'active' : ''}`} onClick={() => setAnalyticsTab('overview')}>Обзор</button>
                <button className={`an-pill ${analyticsTab === 'formats' ? 'active' : ''}`} onClick={() => setAnalyticsTab('formats')}>Форматы</button>
                <button className={`an-pill ${analyticsTab === 'ranking' ? 'active' : ''}`} onClick={() => setAnalyticsTab('ranking')}>Рейтинг</button>
              </div>

              {/* KPI always visible */}
              <div className="an-kpi-grid">
                <div className="an-kpi">
                  <div className="an-kpi-label">Просмотры</div>
                  <div className="an-kpi-val">
                    {(analytics?.kpi?.total_views ?? analytics?.total_views ?? '—')}
                    {analytics?.kpi?.views_delta_approx ? (
                      <span className="an-kpi-badge">+{Number(analytics.kpi.views_delta_approx).toLocaleString('ru-RU')}</span>
                    ) : null}
                  </div>
                  <div className="an-kpi-sub">Сумма по активным роликам · прирост с прошлого синка</div>
                </div>

                <div className="an-kpi">
                  <div className="an-kpi-label">Время просмотра</div>
                  <div className="an-kpi-val">{analytics?.kpi?.watch_hours != null ? `${analytics.kpi.watch_hours} ч` : '—'}</div>
                  <div className="an-progress"><i style={{ width: `${Math.min(100, ((analytics?.kpi?.watch_hours || 0) / 4000) * 100)}%` }} /></div>
                  <div className="an-kpi-sub">До монетизации 4000 ч · сейчас {analytics?.kpi?.watch_hours ?? 0} ч</div>
                </div>

                <div className="an-kpi">
                  <div className="an-kpi-label">Подписчики</div>
                  <div className="an-kpi-val">{analytics?.kpi?.subscribers != null ? Number(analytics.kpi.subscribers).toLocaleString('ru-RU') : '—'}</div>
                  <div className="an-progress blue"><i style={{ width: `${Math.min(100, ((analytics?.kpi?.subscribers || 0) / 1000) * 100)}%` }} /></div>
                  <div className="an-kpi-sub">Пороги 500 / 1000 для партнёрки</div>
                </div>

                <div className={`an-kpi ${analytics?.kpi?.avg_stayed_pct >= 50 ? 'good' : (analytics?.kpi?.avg_stayed_pct != null && analytics?.kpi?.avg_stayed_pct < 40 ? 'warn' : '')}`}>
                  <div className="an-kpi-label">Продолжили смотреть</div>
                  <div className="an-kpi-val" style={{
                    color: analytics?.kpi?.avg_stayed_pct >= 50 ? '#4ade80'
                      : (analytics?.kpi?.avg_stayed_pct != null && analytics?.kpi?.avg_stayed_pct < 40) ? '#f87171' : undefined
                  }}>
                    {analytics?.kpi?.avg_stayed_pct != null ? `${analytics.kpi.avg_stayed_pct}%` : '—'}
                  </div>
                  <div className="an-progress green"><i style={{ width: `${Math.min(100, analytics?.kpi?.avg_stayed_pct || 0)}%` }} /></div>
                  <div className="an-kpi-sub">Среднее по Shorts · зелёный ≥50%, красный &lt;40%</div>
                </div>
              </div>

              {analyticsTab === 'overview' && (
                <>
                  <div className="an-section">
                    <div className="an-section-h">
                      <h3>Динамика канала</h3>
                      <span>Накопительные просмотры по дням синка</span>
                    </div>
                    <div className="an-section-b">
                      {(analytics?.timeline_cumulative || analytics?.timeline || []).length > 0 ? (
                        <div className="an-chart">
                          {(analytics.timeline_cumulative || analytics.timeline).map((d, i) => {
                            const series = analytics.timeline_cumulative || analytics.timeline
                            const max = Math.max(...series.map((x) => x.cumulative || x.views || 0), 1)
                            const val = d.cumulative != null ? d.cumulative : d.views
                            const h = Math.max(8, Math.round((val / max) * 140))
                            return (
                              <div key={i} className="an-chart-col" title={`${d.date}: ${val}`}>
                                <div className="an-chart-val">{val}</div>
                                <div className="an-chart-bar" style={{ height: h }} />
                                <div className="an-chart-lbl">{(d.date || '').slice(5)}</div>
                              </div>
                            )
                          })}
                        </div>
                      ) : (
                        <div className="an-empty">Нет данных для графика — сделай синк YouTube</div>
                      )}
                      {(analytics?.releases || []).length > 0 && (
                        <div className="muted" style={{ marginTop: 14, fontSize: 12 }}>
                          Релизы: {(analytics.releases || []).slice(0, 10).map((r, i) => (
                            <span key={i} style={{ marginRight: 10 }}>
                              {(r.published_at || '').toString().slice(0, 10)} · {r.kind}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="an-section">
                    <div className="an-section-h">
                      <h3>Сводка</h3>
                      <span>{analytics?.active_count ?? '—'} в статистике · {analytics?.excluded_count ?? 0} исключено</span>
                    </div>
                    <div className="an-section-b">
                      <div className="an-kpi-grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0,1fr))' }}>
                        <div className="an-kpi">
                          <div className="an-kpi-label">Лайки</div>
                          <div className="an-kpi-val">{analytics?.total_likes ?? '—'}</div>
                        </div>
                        <div className="an-kpi">
                          <div className="an-kpi-label">Комментарии</div>
                          <div className="an-kpi-val">{analytics?.total_comments ?? '—'}</div>
                        </div>
                        <div className="an-kpi">
                          <div className="an-kpi-label">Собрано роликов</div>
                          <div className="an-kpi-val">{analytics?.episodes_rendered ?? '—'}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {analyticsTab === 'formats' && (
                <div className="an-grid-2">
                  <div className="an-section">
                    <div className="an-section-h">
                      <h3>Shorts · реакция зрителей</h3>
                      <span>Stayed % (продолжили смотреть)</span>
                    </div>
                    <div className="an-section-b">
                      {(analytics?.shorts_battle || []).length === 0 && (
                        <div className="an-empty">Нет Shorts с deep-метриками (≥24ч после публикации)</div>
                      )}
                      {(analytics?.shorts_battle || []).map((v) => {
                        const stayed = v.stayed_pct != null ? Number(v.stayed_pct) : null
                        const avg = v.average_view_percentage != null ? Number(v.average_view_percentage) : null
                        const cls = stayed == null ? '' : stayed >= 50 ? 'good' : stayed < 40 ? 'bad' : ''
                        return (
                          <div key={v.episode_id} className="an-battle-row" onClick={() => openAnalyticsVideo(v.episode_id)} style={{ cursor: 'pointer' }}>
                            <div className="an-battle-title">{v.title || v.episode_id}</div>
                            <div className="an-battle-meta">
                              Stayed {stayed != null ? stayed.toFixed(1) + '%' : '—'}
                              {' · '}досмотр {avg != null ? avg.toFixed(1) + '%' : '—'}
                              {' · '}{(v.views ?? 0).toLocaleString('ru-RU')} views
                            </div>
                            <div className="an-bar-track">
                              <div className={`an-bar-fill ${cls}`} style={{ width: `${Math.min(100, stayed || 0)}%` }} />
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="an-section">
                    <div className="an-section-h">
                      <h3>Long · охват</h3>
                      <span>CTR превью и средний просмотр</span>
                    </div>
                    <div className="an-section-b">
                      {(analytics?.longs_reach || []).length === 0 && (
                        <div className="an-empty">Нет Longs или bulk reach ещё не готов</div>
                      )}
                      {(analytics?.longs_reach || []).map((v) => (
                        <div key={v.episode_id} className="an-battle-row" onClick={() => openAnalyticsVideo(v.episode_id)} style={{ cursor: 'pointer' }}>
                          <div className="an-battle-title">{v.title || v.episode_id}</div>
                          <div className="an-battle-meta">
                            CTR {v.impressions_ctr != null ? Number(v.impressions_ctr).toFixed(2) + '%' : '—'}
                            {' · '}AVD {v.avg_view_duration_sec != null ? Math.round(v.avg_view_duration_sec) + 's' : '—'}
                            {' · '}{(v.views ?? 0).toLocaleString('ru-RU')} views
                          </div>
                          <div className="an-bar-track">
                            <div className="an-bar-fill" style={{ width: `${Math.min(100, (Number(v.impressions_ctr) || 0) * 5)}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {analyticsTab === 'ranking' && (
                <div className="an-section">
                  <div className="an-section-h">
                    <h3>Рейтинг эпизодов</h3>
                    <span>Клик по строке — детали ролика</span>
                  </div>
                  <div className="an-section-b an-table-wrap">
                    <table className="an-table">
                      <thead>
                        <tr>
                          <th>Название</th>
                          <th>Формат</th>
                          <th>Длит.</th>
                          <th>Просмотры</th>
                          <th>Stayed</th>
                          <th>Досмотр</th>
                          <th>Лайки</th>
                          <th>Комменты</th>
                          <th>Статус</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(analytics?.ranking || analytics?.all_videos || []).map((v) => {
                          const stayed = v.stayed_pct
                          const pctCls = stayed >= 50 ? 'an-pct-good' : (stayed != null && stayed < 40 ? 'an-pct-bad' : '')
                          const kind = (v.kind || '').includes('short') ? 'shorts' : 'longs'
                          return (
                            <tr key={v.episode_id || v.id} onClick={() => openAnalyticsVideo(v.episode_id || v.id)}>
                              <td style={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{v.title}</td>
                              <td><span className={`an-tag ${kind}`}>{kind === 'shorts' ? 'Shorts' : 'Long'}</span></td>
                              <td>{v.duration_sec != null ? Math.round(v.duration_sec) + 's' : '—'}</td>
                              <td>{v.views != null ? Number(v.views).toLocaleString('ru-RU') : '—'}</td>
                              <td className={pctCls}>{stayed != null ? Number(stayed).toFixed(1) + '%' : '—'}</td>
                              <td>{v.average_view_percentage != null ? Number(v.average_view_percentage).toFixed(1) + '%' : '—'}</td>
                              <td>{v.likes ?? '—'}</td>
                              <td>{v.comments ?? '—'}</td>
                              <td>{v.status || '—'}</td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                    {(analytics?.ranking || analytics?.all_videos || []).length === 0 && (
                      <div className="an-empty">Пока пусто — привяжи ролики и сделай синк</div>
                    )}
                  </div>
                </div>
              )}

              {analyticsVideo && (
                <div className="an-detail">
                  <div className="an-detail-h">
                    <strong>{analyticsVideo.display?.title || analyticsVideo.episode?.title}</strong>
                    <button className="btn btn-ghost btn-sm" onClick={() => setAnalyticsVideo(null)}>Закрыть</button>
                  </div>
                  <div className="an-kpi-grid">
                    <div className="an-kpi">
                      <div className="an-kpi-label">Просмотры</div>
                      <div className="an-kpi-val">{(analyticsVideo.history?.slice(-1)[0] || {}).views ?? '—'}</div>
                    </div>
                    <div className="an-kpi good">
                      <div className="an-kpi-label">Продолжили смотреть</div>
                      <div className="an-kpi-val">
                        {(analyticsVideo.history?.slice(-1)[0] || {}).stayed_pct != null
                          ? Number(analyticsVideo.history.slice(-1)[0].stayed_pct).toFixed(1) + '%'
                          : '—'}
                      </div>
                    </div>
                    <div className="an-kpi warn">
                      <div className="an-kpi-label">Не стали смотреть</div>
                      <div className="an-kpi-val">
                        {(analyticsVideo.history?.slice(-1)[0] || {}).swipe_away_pct != null
                          ? Number(analyticsVideo.history.slice(-1)[0].swipe_away_pct).toFixed(1) + '%'
                          : '—'}
                      </div>
                    </div>
                    <div className="an-kpi">
                      <div className="an-kpi-label">Ср. просмотр</div>
                      <div className="an-kpi-val">
                        {(analyticsVideo.history?.slice(-1)[0] || {}).avg_view_duration_sec != null
                          ? Math.round(analyticsVideo.history.slice(-1)[0].avg_view_duration_sec) + 's'
                          : '—'}
                      </div>
                    </div>
                  </div>
                  {analyticsVideo.episode?.youtube_id && (
                    <button className="btn btn-primary btn-sm" style={{ marginTop: 14 }} onClick={async () => {
                      await syncYoutube(analyticsVideo.episode)
                      openAnalyticsVideo(analyticsVideo.episode.id)
                    }}>Обновить ролик</button>
                  )}
                </div>
              )}
            </div>
          )}

          {page === 'system' && (
            <>
              <div className="page-title">Система</div>
              <div className="page-sub">Только подключение YouTube и проверка окружения</div>

              <div className="panel" style={{ marginBottom: 16 }}>
                <div className="panel-h">YouTube · OAuth</div>
                <div className="panel-b">
                  <p className="muted" style={{ marginBottom: 10 }}>
                    Подключи Google-аккаунт канала. После этого Контент и Аналитика подтягивают ролики и метрики сами.
                  </p>
                  <div className="row" style={{ marginBottom: 8 }}>
                    <button className="btn btn-ghost btn-sm" onClick={loadOauthStatus}>Обновить статус</button>
                    {oauthStatus?.connected ? (
                      <>
                        <button className="btn btn-primary btn-sm" disabled={ytBusy} onClick={async () => {
                          setYtBusy(true)
                          try {
                            const r = await api('/oauth/youtube/import-channel?max_videos=100', { method: 'POST' })
                            notify(`Импорт: +${r.created || 0} новых, ${r.synced || 0} обновлено`)
                            loadEpisodes()
                          } catch (e) { notify(e.message, true) }
                          finally { setYtBusy(false) }
                        }}>{ytBusy ? 'Импорт…' : 'Импорт роликов с YouTube'}</button>
                        <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={async () => {
                          setYtBusy(true)
                          try {
                            const r = await api('/youtube/dedupe?delete_folders=true', { method: 'POST' })
                            notify(`Дубликаты: удалено ${r.removed || 0}`)
                            loadEpisodes()
                          } catch (e) { notify(e.message, true) }
                          finally { setYtBusy(false) }
                        }}>Удалить дубликаты</button>
                        <button className="btn btn-danger btn-sm" onClick={disconnectYoutubeOauth}>Отключить</button>
                      </>
                    ) : (
                      <button className="btn btn-primary btn-sm" onClick={connectYoutubeOauth}>Подключить Google</button>
                    )}
                  </div>
                  <div className="muted">
                    {oauthStatus == null && 'Нажми «Обновить статус»'}
                    {oauthStatus && !oauthStatus.configured && (
                      <span style={{ color: 'var(--red)' }}>Не настроен client: {oauthStatus.error}</span>
                    )}
                    {oauthStatus?.configured && !oauthStatus.connected && 'Client есть — аккаунт ещё не подключён'}
                    {oauthStatus?.connected && (
                      <span style={{ color: 'var(--green)' }}>
                        Подключено{oauthStatus.channel_title ? `: ${oauthStatus.channel_title}` : ''}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="panel" style={{ marginBottom: 16 }}>
                <div className="panel-h">Обслуживание (редко нужно)</div>
                <div className="panel-b">
                  <p className="muted" style={{ marginBottom: 10 }}>
                    Служебные действия с локальными папками и базой. Не относится к OAuth.
                  </p>
                  <div className="row">
                    <button className="btn btn-ghost btn-sm" onClick={runDoctor}>Проверить окружение</button>
                    <button className="btn btn-ghost btn-sm" onClick={runMigrate} title="Старые папки → storage">Импорт из папок</button>
                    <button className="btn btn-ghost btn-sm" onClick={async () => {
                      try {
                        const r = await api('/fix-titles', { method: 'POST' })
                        notify(r.fixed != null ? `Исправлено названий: ${r.fixed}` : 'Названия обновлены')
                        loadEpisodes()
                      } catch (e) { notify(e.message, true) }
                    }}>Исправить названия</button>
                    <button className="btn btn-ghost btn-sm" onClick={async () => {
                      try {
                        const eps = await api('/episodes')
                        const missing = (eps || []).filter((e) => !e.has_preview && !e.has_thumb)
                        notify(missing.length ? `Без превью: ${missing.length} роликов` : 'Превью есть у всех роликов')
                      } catch (e) { notify(e.message, true) }
                    }}>Проверить превью</button>
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-h">
                  <span>Статус окружения</span>
                  <span className="muted">{doctor?.ok === false ? 'есть проблемы' : doctor ? 'OK' : '—'}</span>
                </div>
                <div className="panel-b">
                  {doctor ? (
                    <pre className="desc-block" style={{ maxHeight: 280 }}>{JSON.stringify(doctor, null, 2)}</pre>
                  ) : (
                    <div className="muted">Нажми «Проверить окружение», чтобы увидеть версии MoviePy, ffmpeg и т.д.</div>
                  )}
                </div>
              </div>
            </>
          )}

{showNewChannel && (
        <Modal
          title="Новый канал"
          onClose={() => setShowNewChannel(false)}
          footer={
            <>
              <button className="btn btn-ghost" onClick={() => setShowNewChannel(false)}>Отмена</button>
              <button className="btn btn-primary" onClick={createChannel} disabled={!newChannelName.trim()}>Создать канал</button>
            </>
          }
        >
          <div className="field">
            <label>Название канала</label>
            <input
              autoFocus
              value={newChannelName}
              onChange={(e) => setNewChannelName(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') createChannel() }}
              placeholder="Например, uTeam-Studio"
            />
          </div>
        </Modal>
      )}

      {showNewEpisode && (
        <Modal
          title="Новое видео"
          onClose={() => setShowNewEpisode(false)}
          footer={
            <>
              <button className="btn btn-ghost" onClick={() => setShowNewEpisode(false)}>Отмена</button>
              <button className="btn btn-primary" onClick={createEpisode} disabled={!newEpTitle.trim() || !newEpChannel}>Создать видео</button>
            </>
          }
        >
          <div className="field">
            <label>Название видео</label>
            <input
              autoFocus
              value={newEpTitle}
              onChange={(e) => setNewEpTitle(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') createEpisode() }}
              placeholder="Тема или название ролика"
            />
          </div>
          <div className="field">
            <label>Канал</label>
            <select
              value={newEpChannel ?? ''}
              onChange={(e) => setNewEpChannel(e.target.value ? Number(e.target.value) : null)}
              disabled={!channels.length}
            >
              <option value="">Выбери канал</option>
              {channels.map((channel) => (
                <option key={channel.id} value={channel.id}>{channel.name}</option>
              ))}
            </select>
            {!channels.length && (
              <div className="hint">Сначала создай канал.</div>
            )}
          </div>
          <div className="field">
            <label>Формат</label>
            <select value={newEpKind} onChange={(e) => setNewEpKind(e.target.value)}>
              <option value="shorts">YouTube Shorts</option>
              <option value="long">Длинное видео</option>
            </select>
          </div>
        </Modal>
      )}

      {showTheater && activeJobId && (
        <RenderTheater
          job={jobs.find((j) => Number(j.id) === Number(activeJobId)) || { id: activeJobId, status: 'running', log: [], preview: !!preview }}
          episodeTitle={renderTitle}
          mode={theaterMode}
          onMode={setTheaterMode}
          onCancel={() => cancelJob(activeJobId)}
          onClose={() => setShowTheater(false)}
        />
      )}

      {toast && <div className={`toast ${toast.err ? 'err' : ''}`}>{toast.msg}</div>}

      <input
        ref={fileRef}
        type="file"
        accept=".mp3,audio/mpeg,audio/wav,.wav,.m4a"
        style={{ display: 'none' }}
        onChange={(e) => uploadVoice(e.target.files?.[0])}
      />
    </div>
      </div>
    </div>
  )
}
