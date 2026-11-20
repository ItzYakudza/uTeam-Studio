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

function RenderTheater({ job, episodeTitle, onClose, onCancel, mode = 'full', onMode }) {
  if (!job) return null
  const logs = Array.isArray(job.log) ? job.log : []
  const { current, done } = stageFromLogs(logs)
  const isDone = job.status === 'done'
  const isErr = job.status === 'error' || job.status === 'cancelled'
  const stageList = RENDER_STAGES
  let progress = 8
  if (isDone || job.status === 'cancelled' || job.status === 'error') progress = 100
  else {
    const idx = stageList.findIndex((s) => s.id === current)
    progress = Math.min(95, Math.max(8, ((idx + 1) / stageList.length) * 100))
  }
  const plainLogs = logs.filter((l) => typeof l === 'string' && !l.startsWith('STAGE:')).slice(-8)
  const statusLabel =
    job.status === 'done' ? 'Готово' :
    job.status === 'cancelled' ? 'Отменено' :
    job.status === 'error' ? 'Ошибка' :
    job.status === 'queued' ? 'В очереди' : 'Идёт сборка'

  if (mode === 'mini') {
    return (
      <div className="render-mini" onClick={() => onMode && onMode('full')}>
        <div className="render-mini-bar"><i style={{ width: progress + '%' }} /></div>
        <div className="render-mini-body">
          <div>
            <strong>{episodeTitle || 'Рендер'}</strong>
            <div className="muted">{statusLabel} · {Math.round(progress)}%</div>
          </div>
          <div className="row">
            {!isDone && job.status !== 'cancelled' && job.status !== 'error' && (
              <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); onCancel && onCancel() }}>Отменить</button>
            )}
            <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); onMode && onMode('full') }}>Развернуть</button>
            <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); onClose && onClose() }}>Скрыть</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="render-theater">
      <div className="render-card" onClick={(e) => e.stopPropagation()}>
        <div className={`render-hero ${isDone ? 'done' : ''} ${isErr ? 'err' : ''}`}>
          <div className="render-hero-inner">
            <div className="render-ring">{isDone ? '✓' : job.status === 'cancelled' ? '✕' : ''}</div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>{statusLabel}</div>
          </div>
          {!isDone && !isErr && <div className="film-strip" />}
        </div>
        <div className="render-body">
          <div className="render-title">{episodeTitle || 'Рендер'}</div>
          <div className="render-sub">
            {job.preview ? 'Preview' : 'Full quality'} · job #{job.id}
          </div>
          <div className={`render-bar ${!isDone && !isErr && progress < 20 ? 'indeterminate' : ''}`}>
            <i style={{ width: progress + '%' }} />
          </div>
          <div className="render-stages">
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
            <div className="render-log">
              {plainLogs.map((l, i) => (
                <div key={i}>{l}</div>
              ))}
            </div>
          )}
          <div className="render-actions">
            {!isDone && job.status !== 'cancelled' && job.status !== 'error' && (
              <button className="btn btn-danger" onClick={onCancel}>Отменить рендер</button>
            )}
            {!isDone && job.status !== 'cancelled' && job.status !== 'error' && (
              <button className="btn btn-ghost" onClick={() => onMode && onMode('mini')}>Свернуть</button>
            )}
            {(isDone || isErr) && (
              <button className="btn btn-primary" onClick={onClose}>{isDone ? 'Готово' : 'Закрыть'}</button>
            )}
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
  const [preview, setPreview] = useState(true)

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
    const t = setInterval(() => {
      loadJobs()
      loadEpisodes()
    }, 3000)
    return () => clearInterval(t)
  }, [loadChannels, loadEpisodes, loadJobs])

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
      notify(preview ? 'Preview запущен' : 'Рендер запущен')
      loadJobs()
    } catch (e) {
      notify(e.message, true)
    }
  }

  async function startSheet(ep) {
    try {
      await api('/sheet', { method: 'POST', body: JSON.stringify({ episode_id: ep.id }) })
      notify('Contact sheet запущен')
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
      if (page === 'analytics') setAnalytics(await api('/analytics/summary'))
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
      notify(`Синк · ${res.youtube?.views ?? 0} views`)
      loadEpisodes()
      if (page === 'analytics') setAnalytics(await api('/analytics/summary'))
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
      setAnalytics(await api('/analytics/summary'))
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
      try { setAnalytics(await api('/analytics/summary')) } catch {}
    } catch (e) {
      notify(e.message, true)
    } finally {
      setYtBusy(false)
    }
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
      notify(`Синк: ${res.synced} ок, ${res.skipped} без ссылки, ${res.failed} ошибок`)
      loadEpisodes()
      setAnalytics(await api('/analytics/summary'))
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
        <div
          className={`nav-item ${page === 'analytics' ? 'active' : ''}`}
          onClick={async () => {
            setPage('analytics')
            try { setAnalytics(await api('/analytics/summary')) } catch (e) { notify(e.message, true) }
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

        <div className="section-label">Каналы</div>
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
          <button className="btn btn-primary" onClick={() => setShowNewEpisode(true)}>
            + Новое видео
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => setShowNewChannel(true)}>
            + Канал
          </button>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <input
            className="search"
            placeholder="Поиск по названию, тегам…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <div className="row">
            <label className="muted" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <input type="checkbox" checked={preview} onChange={(e) => setPreview(e.target.checked)} />
              Preview
            </label>
            <button className="btn btn-ghost btn-sm" onClick={() => { loadEpisodes(); loadChannels() }}>
              Обновить
            </button>
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
              <div className="page-sub">Как YouTube Studio — список роликов, статусы, быстрые действия</div>

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
                        {ep.has_video && <span className="thumb-badge">MP4</span>}
                      </div>
                      <div className="video-body">
                        <div className="video-title">{ep.title}</div>
                        <div className="video-meta">
                          <span>{ep.channel_name}</span>
                          <span>·</span>
                          <span>{ep.has_voice ? 'voice' : 'no voice'}</span>
                          <span>·</span>
                          <span>{ep.youtube_id ? 'YT' : 'no YT'}</span>
                          {ep.yt_views != null && <span>· {ep.yt_views} views</span>}
                        </div>
                        <div className="video-actions" onClick={(e) => e.stopPropagation()}>
                          <button className="btn btn-sm btn-success" disabled={!ep.has_voice || !ep.has_scenes} onClick={() => startRender(ep)}>
                            Собрать
                          </button>
                          <button className="btn btn-sm btn-ghost" onClick={() => openEpisode(ep)}>Открыть</button>
                          <button className="btn btn-sm btn-danger" onClick={() => removeEpisode(ep)}>×</button>
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
                    {preview ? 'Preview' : 'Собрать'}
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
                        <button className="btn btn-primary btn-sm" disabled={ytBusy} onClick={() => linkYoutube(selected, false)}>
                          {ytBusy ? '…' : 'Привязать + статистика'}
                        </button>
                        <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={() => linkYoutube(selected, true)}>
                          + обновить title
                        </button>
                        {selected.youtube_id && (
                          <button className="btn btn-ghost btn-sm" disabled={ytBusy} onClick={() => syncYoutube(selected)}>
                            Синк
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
                        Собрать ролик {preview ? '(preview)' : ''}
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
                <button className="btn btn-ghost" onClick={runMigrate}>Импорт старых папок</button>
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
              <div className="page-title">Рендеры</div>
              <div className="page-sub">Активные и недавние сборки. Можно открыть на весь экран, свернуть или отменить.</div>
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
                              {j.status}
                            </span>
                            <span>·</span>
                            <span>{j.kind}</span>
                            {j.preview ? <span>· preview</span> : null}
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
            <>
              <div className="page-title">Аналитика</div>
              <div className="page-sub">
                Только данные с YouTube. Ручной ввод отключён. Можно исключить ролик из общей статистики.
              </div>
              <div className="row" style={{ marginBottom: 16 }}>
                <button className="btn btn-primary" disabled={ytBusy} onClick={syncAllYoutube}>
                  {ytBusy ? 'Синк…' : 'Синк всех с YouTube'}
                </button>
                <a className="btn btn-ghost" href={`${API}/analytics/export?format=json`} target="_blank" rel="noreferrer">Export JSON</a>
                <a className="btn btn-ghost" href={`${API}/analytics/export?format=md`} target="_blank" rel="noreferrer">Export MD</a>
              </div>

              <div className="stats">
                <div className="stat"><div className="stat-val">{analytics?.total_views ?? '—'}</div><div className="stat-label">Просмотры (активные)</div></div>
                <div className="stat"><div className="stat-val">{analytics?.total_likes ?? '—'}</div><div className="stat-label">Лайки</div></div>
                <div className="stat"><div className="stat-val">{analytics?.total_comments ?? '—'}</div><div className="stat-label">Комменты</div></div>
                <div className="stat"><div className="stat-val">{analytics?.active_count ?? '—'}</div><div className="stat-label">В общей статистике</div></div>
                <div className="stat"><div className="stat-val">{analytics?.excluded_count ?? '—'}</div><div className="stat-label">Исключено</div></div>
                <div className="stat"><div className="stat-val">{analytics?.episodes_rendered ?? '—'}</div><div className="stat-label">Собрано роликов</div></div>
              </div>

              {(analytics?.timeline || []).length > 0 && (
                <div className="panel" style={{ marginBottom: 16 }}>
                  <div className="panel-h">Динамика просмотров по дням синка</div>
                  <div className="panel-b">
                    <div className="chart-bars">
                      {analytics.timeline.map((d) => {
                        const max = Math.max(...analytics.timeline.map((x) => x.views), 1)
                        const h = Math.max(6, Math.round((d.views / max) * 140))
                        return (
                          <div key={d.date} className="chart-col" title={`${d.date}: ${d.views}`}>
                            <div className="chart-val">{d.views > 999 ? (d.views/1000).toFixed(1)+'k' : d.views}</div>
                            <div className="chart-bar" style={{ height: h }} />
                            <div className="chart-label">{d.date.slice(5)}</div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>
              )}

              <div className="panel">
                <div className="panel-h">Видео</div>
                <div className="panel-b" style={{ padding: 0 }}>
                  <table className="analytics-table">
                    <thead>
                      <tr>
                        <th>Название</th>
                        <th>Канал</th>
                        <th>Views</th>
                        <th>Likes</th>
                        <th>Comments</th>
                        <th>В общей</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {(analytics?.all_videos || analytics?.top_videos || []).map((v) => (
                        <tr key={v.episode_id} className={!v.include_in_aggregate ? 'row-muted' : ''}>
                          <td>
                            <button className="linkish" onClick={() => openAnalyticsVideo(v.episode_id)}>
                              {v.title}
                            </button>
                          </td>
                          <td className="muted">{v.channel_name}</td>
                          <td>{v.views}</td>
                          <td>{v.likes}</td>
                          <td>{v.comments}</td>
                          <td>
                            <button
                              className={`chip ${v.include_in_aggregate ? 'active' : ''}`}
                              onClick={() => toggleAggregate(v.episode_id, !v.include_in_aggregate)}
                            >
                              {v.include_in_aggregate ? 'да' : 'нет'}
                            </button>
                          </td>
                          <td>
                            <button className="btn btn-sm btn-ghost" onClick={() => openAnalyticsVideo(v.episode_id)}>Подробнее</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {(analytics?.all_videos || analytics?.top_videos || []).length === 0 && (
                    <div className="empty">Нет данных — привяжи YouTube и сделай синк</div>
                  )}
                </div>
              </div>

              {analyticsVideo && (
                <div className="panel" style={{ marginTop: 16 }}>
                  <div className="panel-h">
                    <span>{analyticsVideo.display?.title || analyticsVideo.episode?.title}</span>
                    <button className="btn btn-ghost btn-sm" onClick={() => setAnalyticsVideo(null)}>Закрыть</button>
                  </div>
                  <div className="panel-b">
                    <div className="stats" style={{ marginBottom: 16 }}>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).views ?? '—'}</div><div className="stat-label">Просмотры</div></div>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).likes ?? '—'}</div><div className="stat-label">Лайки</div></div>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).comments ?? '—'}</div><div className="stat-label">Комменты</div></div>
                      <div className="stat"><div className="stat-val">{analyticsVideo.display?.duration_sec ? Math.round(analyticsVideo.display.duration_sec)+'s' : '—'}</div><div className="stat-label">Длительность</div></div>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).avg_view_duration_sec != null ? Math.round((analyticsVideo.history.slice(-1)[0].avg_view_duration_sec))+'s' : '—'}</div><div className="stat-label">Ср. просмотр</div></div>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).average_view_percentage != null ? Number(analyticsVideo.history.slice(-1)[0].average_view_percentage).toFixed(1)+'%' : '—'}</div><div className="stat-label">% досмотра</div></div>
                      <div className="stat"><div className="stat-val">{(analyticsVideo.history?.slice(-1)[0] || {}).swipe_away_pct != null ? Number(analyticsVideo.history.slice(-1)[0].swipe_away_pct).toFixed(1)+'%' : '—'}</div><div className="stat-label">Swipe away</div></div>
                    </div>
                    <div className="row" style={{ marginBottom: 12 }}>
                      <span className="muted">YouTube:</span>
                      {analyticsVideo.display?.youtube_url ? (
                        <a href={analyticsVideo.display.youtube_url} target="_blank" rel="noreferrer">{analyticsVideo.display.youtube_id}</a>
                      ) : 'не привязан'}
                      <span className="muted">· privacy: {analyticsVideo.meta?.privacy || '—'}</span>
                      <span className="muted">· published: {analyticsVideo.meta?.published_at || '—'}</span>
                      <span className="muted">· available: {String(analyticsVideo.status?.available)}</span>
                    </div>
                    <div className="row" style={{ marginBottom: 16 }}>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => toggleAggregate(analyticsVideo.episode.id, !analyticsVideo.include_in_aggregate)}
                      >
                        {analyticsVideo.include_in_aggregate ? 'Исключить из общей статистики' : 'Вернуть в общую статистику'}
                      </button>
                      {analyticsVideo.episode?.youtube_id && (
                        <button className="btn btn-primary btn-sm" disabled={ytBusy} onClick={async () => {
                          await syncYoutube(analyticsVideo.episode)
                          openAnalyticsVideo(analyticsVideo.episode.id)
                        }}>Обновить с YouTube</button>
                      )}
                    </div>
                    {(analyticsVideo.history || []).length > 0 ? (
                      <div className="chart-bars">
                        {analyticsVideo.history.map((h, idx) => {
                          const max = Math.max(...analyticsVideo.history.map((x) => x.views || 0), 1)
                          const hgt = Math.max(6, Math.round(((h.views || 0) / max) * 140))
                          return (
                            <div key={idx} className="chart-col" title={`${h.date || h.ts}: ${h.views} views`}>
                              <div className="chart-val">{h.views}</div>
                              <div className="chart-bar" style={{ height: hgt }} />
                              <div className="chart-label">{(h.date || '').slice(5) || idx}</div>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <div className="muted">Истории синка пока нет</div>
                    )}
                    {analyticsVideo.display?.description && (
                      <div style={{ marginTop: 16 }}>
                        <div className="muted" style={{ marginBottom: 6 }}>Описание</div>
                        <pre className="desc-block">{analyticsVideo.display.description}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}

{page === 'system' && (
            <>
              <div className="page-title">Система</div>
              <div className="page-sub">Проверка окружения, OAuth YouTube, база данных</div>

              <div className="panel" style={{ marginBottom: 16 }}>
                <div className="panel-h">YouTube Studio OAuth</div>
                <div className="panel-b">
                  <p className="muted" style={{ marginBottom: 10 }}>
                    Для среднего времени просмотра, % досмотра, shares и подписчиков.
                    OAuth Web client в Google Cloud, redirect:
                    <code> http://127.0.0.1:5050/api/oauth/youtube/callback</code>
                    Ключи в <code>web/youtube_oauth.json</code>
                  </p>
                  <div className="row" style={{ marginBottom: 8 }}>
                    <button className="btn btn-ghost btn-sm" onClick={loadOauthStatus}>Обновить статус</button>
                    {oauthStatus?.connected ? (
                      <button className="btn btn-danger btn-sm" onClick={disconnectYoutubeOauth}>Отключить</button>
                    ) : (
                      <button className="btn btn-primary btn-sm" onClick={connectYoutubeOauth}>Подключить Google</button>
                    )}
                  </div>
                  <div className="muted">
                    {oauthStatus == null && 'Нажми «Обновить статус»'}
                    {oauthStatus && !oauthStatus.configured && (
                      <span style={{ color: 'var(--red)' }}>Не настроен client: {oauthStatus.error}</span>
                    )}
                    {oauthStatus?.configured && !oauthStatus.connected && 'Client есть — аккаунт не подключён'}
                    {oauthStatus?.connected && (
                      <span style={{ color: 'var(--green)' }}>
                        Подключено: {oauthStatus.channel_title || oauthStatus.channel_id}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="row" style={{ marginBottom: 16 }}>
                <button className="btn btn-ghost" onClick={runDoctor}>Проверить</button>
                <button className="btn btn-ghost" onClick={runMigrate}>Импорт из channels/</button>
                <button className="btn btn-primary" onClick={async () => {
                  try {
                    const r = await api('/fix-titles', { method: 'POST' })
                    notify('Названия обновлены: ' + r.fixed)
                    loadEpisodes()
                  } catch (e) { notify(e.message, true) }
                }}>Исправить названия</button>
                <button className="btn btn-ghost" onClick={async () => {
                  try {
                    const r = await api('/regenerate-thumbs', { method: 'POST' })
                    notify('Превью: ' + r.thumbs)
                    loadEpisodes()
                  } catch (e) { notify(e.message, true) }
                }}>Проверить превью-файлы</button>
              </div>
              {doctor && (
                <div className="panel">
                  <div className="panel-h">
                    Статус:{' '}
                    <span style={{ color: doctor.ok ? 'var(--green)' : 'var(--red)' }}>
                      {doctor.ok ? 'OK' : 'Есть проблемы'}
                    </span>
                  </div>
                  <div className="panel-b">
                    {doctor.issues?.length > 0 && (
                      <ul style={{ marginBottom: 12, paddingLeft: 18, color: 'var(--red)' }}>
                        {doctor.issues.map((x, i) => (
                          <li key={i}>{x}</li>
                        ))}
                      </ul>
                    )}
                    <pre style={{ fontSize: 12, overflow: 'auto' }}>{JSON.stringify(doctor.info, null, 2)}</pre>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* bottom bar removed — use «Рендеры» tab + theater */}
      </div>

      {showNewChannel && (
        <Modal
          title="Новый канал"
          onClose={() => setShowNewChannel(false)}
          footer={
            <>
              <button className="btn btn-ghost" onClick={() => setShowNewChannel(false)}>Отмена</button>
              <button className="btn btn-primary" onClick={createChannel}>Создать</button>
            </>
          }
        >
          <div className="field">
            <label>Название</label>
            <input value={newChannelName} onChange={(e) => setNewChannelName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && createChannel()} autoFocus placeholder="например zuppy" />
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
              <button className="btn btn-primary" onClick={createEpisode}>Создать</button>
            </>
          }
        >
          <div className="field">
            <label>Канал</label>
            <select value={newEpChannel || ''} onChange={(e) => setNewEpChannel(Number(e.target.value))}>
              {channels.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Тип</label>
            <select value={newEpKind} onChange={(e) => setNewEpKind(e.target.value)}>
              <option value="shorts">Shorts</option>
              <option value="long">Long</option>
            </select>
          </div>
          <div className="field">
            <label>Название</label>
            <input value={newEpTitle} onChange={(e) => setNewEpTitle(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && createEpisode()} autoFocus placeholder="Stopped Clock Illusion" />
          </div>
        </Modal>
      )}

      {showTheater && activeJobId && (
        <RenderTheater
          job={jobs.find((j) => j.id === activeJobId) || { id: activeJobId, status: 'running', log: [], preview }}
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
  )
}
