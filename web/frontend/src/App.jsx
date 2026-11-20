import React, { useState, useEffect, useCallback, useRef } from 'react'

const API = '/api'

async function api(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { 'Content-Type': 'application/json', ...opts.headers },
    ...opts,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || res.statusText)
  }
  return res.json()
}

function Toggle({ on, onChange, label }) {
  return (
    <div className="toggle-row">
      <div className={`toggle ${on ? 'on' : ''}`} onClick={() => onChange(!on)} role="switch" aria-checked={on} />
      {label && <span className="toggle-label">{label}</span>}
    </div>
  )
}

function Modal({ title, children, onClose, footer }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">{title}</div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  )
}

export default function App() {
  const [channels, setChannels] = useState([])
  const [selectedChannel, setSelectedChannel] = useState(null)
  const [selectedEp, setSelectedEp] = useState(null)
  const [view, setView] = useState('list') // list | editor
  const [preview, setPreview] = useState(false)
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // modals
  const [showNewChannel, setShowNewChannel] = useState(false)
  const [showNewEpisode, setShowNewEpisode] = useState(false)
  const [newChannelName, setNewChannelName] = useState('')
  const [newEpKind, setNewEpKind] = useState('shorts')
  const [newEpName, setNewEpName] = useState('')

  // editor
  const [scriptContent, setScriptContent] = useState('')
  const [scenesContent, setScenesContent] = useState('')
  const [activeTab, setActiveTab] = useState('script') // script | scenes
  const [saving, setSaving] = useState(false)
  const [dirty, setDirty] = useState(false)

  const pollRef = useRef(null)

  const loadChannels = useCallback(async () => {
    try {
      setError(null)
      const data = await api('/channels')
      setChannels(data)
      if (selectedChannel) {
        const updated = data.find((c) => c.name === selectedChannel)
        if (updated) {
          // refresh selected ep if needed
          if (selectedEp) {
            const ep = updated.episodes.find((e) => e.path === selectedEp.path)
            if (ep) setSelectedEp(ep)
          }
        }
      } else if (data.length && !selectedChannel) {
        setSelectedChannel(data[0].name)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [selectedChannel, selectedEp])

  useEffect(() => {
    loadChannels()
  }, [])

  // poll jobs
  useEffect(() => {
    const tick = async () => {
      try {
        const list = await api('/jobs')
        setJobs(list)
        const running = list.some((j) => j.status === 'running' || j.status === 'queued')
        if (!running && pollRef.current) {
          // still poll occasionally
        }
        // refresh channels when a job finishes
        if (list.some((j) => j.status === 'done' || j.status === 'error')) {
          loadChannels()
        }
      } catch {}
    }
    tick()
    pollRef.current = setInterval(tick, 2500)
    return () => clearInterval(pollRef.current)
  }, [loadChannels])

  const currentChannel = channels.find((c) => c.name === selectedChannel)
  const episodes = currentChannel?.episodes || []

  async function handleCreateChannel() {
    if (!newChannelName.trim()) return
    try {
      await api('/channels', { method: 'POST', body: JSON.stringify({ name: newChannelName }) })
      setShowNewChannel(false)
      setNewChannelName('')
      await loadChannels()
      setSelectedChannel(newChannelName.trim().toLowerCase().replace(/ /g, '_'))
    } catch (e) {
      alert(e.message)
    }
  }

  async function handleDeleteChannel(name) {
    if (!confirm(`Удалить канал «${name}» и все эпизоды?`)) return
    try {
      await api(`/channels/${name}`, { method: 'DELETE' })
      if (selectedChannel === name) {
        setSelectedChannel(null)
        setSelectedEp(null)
        setView('list')
      }
      await loadChannels()
    } catch (e) {
      alert(e.message)
    }
  }

  async function handleCreateEpisode() {
    if (!newEpName.trim() || !selectedChannel) return
    try {
      const res = await api('/episodes', {
        method: 'POST',
        body: JSON.stringify({
          channel: selectedChannel,
          kind: newEpKind,
          short_name: newEpName,
        }),
      })
      setShowNewEpisode(false)
      setNewEpName('')
      await loadChannels()
      setSelectedEp(res.episode)
      openEditor(res.episode)
    } catch (e) {
      alert(e.message)
    }
  }

  async function handleDeleteEpisode(ep) {
    if (!confirm(`Удалить эпизод «${ep.name}»?`)) return
    try {
      await api(`/episodes?path=${encodeURIComponent(ep.path)}`, { method: 'DELETE' })
      if (selectedEp?.path === ep.path) {
        setSelectedEp(null)
        setView('list')
      }
      await loadChannels()
    } catch (e) {
      alert(e.message)
    }
  }

  async function openEditor(ep) {
    setSelectedEp(ep)
    setView('editor')
    setDirty(false)
    try {
      const [script, scenes] = await Promise.all([
        api(`/file?path=${encodeURIComponent(ep.path + '/script.txt')}`).catch(() => ({ content: '' })),
        api(`/file?path=${encodeURIComponent(ep.path + '/scenes.py')}`).catch(() => ({ content: '' })),
      ])
      setScriptContent(script.content || '')
      setScenesContent(scenes.content || '')
    } catch (e) {
      alert(e.message)
    }
  }

  async function saveCurrent() {
    if (!selectedEp) return
    setSaving(true)
    try {
      if (activeTab === 'script') {
        await api(`/file?path=${encodeURIComponent(selectedEp.path + '/script.txt')}`, {
          method: 'PUT',
          body: JSON.stringify({ content: scriptContent }),
        })
      } else {
        await api(`/file?path=${encodeURIComponent(selectedEp.path + '/scenes.py')}`, {
          method: 'PUT',
          body: JSON.stringify({ content: scenesContent }),
        })
      }
      setDirty(false)
    } catch (e) {
      alert(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function saveAll() {
    if (!selectedEp) return
    setSaving(true)
    try {
      await Promise.all([
        api(`/file?path=${encodeURIComponent(selectedEp.path + '/script.txt')}`, {
          method: 'PUT',
          body: JSON.stringify({ content: scriptContent }),
        }),
        api(`/file?path=${encodeURIComponent(selectedEp.path + '/scenes.py')}`, {
          method: 'PUT',
          body: JSON.stringify({ content: scenesContent }),
        }),
      ])
      setDirty(false)
    } catch (e) {
      alert(e.message)
    } finally {
      setSaving(false)
    }
  }

  async function startRender(ep) {
    try {
      const res = await api('/render', {
        method: 'POST',
        body: JSON.stringify({ path: ep.path, preview }),
      })
      setJobs((j) => [...j, { id: res.job_id, status: 'queued', path: ep.path }])
    } catch (e) {
      alert(e.message)
    }
  }

  async function startSheet(ep) {
    try {
      const res = await api('/sheet', {
        method: 'POST',
        body: JSON.stringify({ path: ep.path }),
      })
      setJobs((j) => [...j, { id: res.job_id, status: 'queued', path: ep.path }])
    } catch (e) {
      alert(e.message)
    }
  }

  function download(path) {
    window.open(`${API}/download?path=${encodeURIComponent(path)}`, '_blank')
  }

  const recentJobs = [...jobs].reverse().slice(0, 5)

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">uT</div>
          <div>
            <div className="brand-text">uTeam Studio</div>
            <div className="brand-sub">YouTube production</div>
          </div>
        </div>

        <div className="section-label">Каналы</div>
        {channels.map((ch) => (
          <div
            key={ch.name}
            className={`channel-item ${selectedChannel === ch.name ? 'active' : ''}`}
            onClick={() => {
              setSelectedChannel(ch.name)
              setView('list')
              setSelectedEp(null)
            }}
          >
            <span>{ch.name}</span>
            <span className="counts">
              {ch.shorts_count}s / {ch.longs_count}l
            </span>
          </div>
        ))}

        <div className="mt-3" style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <button className="btn btn-ghost" onClick={() => setShowNewChannel(true)}>
            + Новый канал
          </button>
          {selectedChannel && (
            <button className="btn btn-danger btn-sm" onClick={() => handleDeleteChannel(selectedChannel)}>
              Удалить канал
            </button>
          )}
        </div>

        <div className="section-label mt-3">Рендер</div>
        <div style={{ padding: '4px 8px' }}>
          <Toggle on={preview} onChange={setPreview} label={preview ? 'Preview (быстрый)' : 'Full quality'} />
        </div>
      </aside>

      {/* Main */}
      <div className="main">
        <header className="topbar">
          <div className="row gap-sm">
            {view === 'editor' && (
              <button className="btn btn-ghost btn-sm" onClick={() => setView('list')}>
                ← К списку
              </button>
            )}
            <strong style={{ fontSize: 14 }}>
              {view === 'editor' && selectedEp
                ? selectedEp.name
                : selectedChannel
                ? `Канал: ${selectedChannel}`
                : 'uTeam Studio'}
            </strong>
          </div>
          <div className="row gap-sm">
            {view === 'list' && selectedChannel && (
              <button className="btn btn-primary btn-sm" onClick={() => setShowNewEpisode(true)}>
                + Эпизод
              </button>
            )}
            {view === 'editor' && (
              <>
                <button className="btn btn-ghost btn-sm" onClick={saveAll} disabled={saving || !dirty}>
                  {saving ? 'Сохранение…' : 'Сохранить всё'}
                </button>
                <button className="btn btn-success btn-sm" onClick={() => startRender(selectedEp)}>
                  Рендер {preview ? '(preview)' : ''}
                </button>
              </>
            )}
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="card mb-2" style={{ borderColor: 'var(--danger)' }}>
              <div className="card-body text-sm" style={{ color: 'var(--danger)' }}>
                Ошибка API: {error}. Убедись, что backend запущен на :5050
              </div>
            </div>
          )}

          {loading ? (
            <div className="empty">Загрузка…</div>
          ) : view === 'list' ? (
            !selectedChannel ? (
              <div className="empty">
                <h3>Нет выбранного канала</h3>
                <p>Создай канал слева или выбери существующий</p>
              </div>
            ) : episodes.length === 0 ? (
              <div className="empty">
                <h3>Пока нет эпизодов</h3>
                <p className="mb-2">Создай первый ролик для канала «{selectedChannel}»</p>
                <button className="btn btn-primary" onClick={() => setShowNewEpisode(true)}>
                  + Создать эпизод
                </button>
              </div>
            ) : (
              <div className="ep-grid">
                {episodes.map((ep) => (
                  <div
                    key={ep.path}
                    className={`ep-card ${selectedEp?.path === ep.path ? 'selected' : ''}`}
                    onClick={() => setSelectedEp(ep)}
                  >
                    <div className="ep-name">{ep.name}</div>
                    <div className="ep-meta">
                      <span className={`badge kind-${ep.kind}`}>{ep.kind}</span>
                      <span className={`badge ${ep.has_script ? 'ok' : 'warn'}`}>
                        {ep.has_script ? 'script' : 'no script'}
                      </span>
                      <span className={`badge ${ep.has_scenes ? 'ok' : 'warn'}`}>
                        {ep.has_scenes ? 'scenes' : 'no scenes'}
                      </span>
                      <span className={`badge ${ep.has_voice ? 'ok' : 'warn'}`}>
                        {ep.has_voice ? 'voice' : 'no voice'}
                      </span>
                      {ep.has_final && <span className="badge ok">mp4</span>}
                    </div>
                    <div className="ep-actions" onClick={(e) => e.stopPropagation()}>
                      <button className="btn btn-ghost btn-sm" onClick={() => openEditor(ep)}>
                        Редактор
                      </button>
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => startRender(ep)}
                        disabled={!ep.has_scenes || !ep.has_voice}
                        title={!ep.has_voice ? 'Нужен voiceover.mp3' : ''}
                      >
                        Рендер
                      </button>
                      <button className="btn btn-ghost btn-sm" onClick={() => startSheet(ep)} disabled={!ep.has_voice}>
                        Sheet
                      </button>
                      {ep.has_final && (
                        <button
                          className="btn btn-ghost btn-sm"
                          onClick={() => download(`${ep.path}/build/${ep.final_name}`)}
                        >
                          MP4
                        </button>
                      )}
                      <button className="btn btn-danger btn-sm" onClick={() => handleDeleteEpisode(ep)}>
                        Удал.
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            /* Editor view */
            <div className="editor-layout">
              <div className="editor-panel">
                <div className="editor-toolbar">
                  <button
                    className={`btn btn-sm ${activeTab === 'script' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setActiveTab('script')}
                  >
                    script.txt
                  </button>
                  <button
                    className={`btn btn-sm ${activeTab === 'scenes' ? 'btn-primary' : 'btn-ghost'}`}
                    onClick={() => setActiveTab('scenes')}
                  >
                    scenes.py
                  </button>
                  <span className="file-name">
                    {selectedEp?.path}/{activeTab === 'script' ? 'script.txt' : 'scenes.py'}
                  </span>
                  <button className="btn btn-ghost btn-sm" onClick={saveCurrent} disabled={saving || !dirty}>
                    {saving ? '…' : 'Сохранить'}
                  </button>
                </div>
                <textarea
                  className="editor-area"
                  value={activeTab === 'script' ? scriptContent : scenesContent}
                  onChange={(e) => {
                    setDirty(true)
                    if (activeTab === 'script') setScriptContent(e.target.value)
                    else setScenesContent(e.target.value)
                  }}
                  spellCheck={false}
                />
              </div>

              <div className="editor-panel">
                <div className="editor-toolbar">
                  <span className="card-title">Инфо и действия</span>
                </div>
                <div className="card-body">
                  {selectedEp && (
                    <>
                      <div className="ep-meta mb-2">
                        <span className={`badge kind-${selectedEp.kind}`}>{selectedEp.kind}</span>
                        <span className={`badge ${selectedEp.has_voice ? 'ok' : 'warn'}`}>
                          {selectedEp.has_voice ? 'voiceover.mp3 ✓' : 'Нет voiceover.mp3'}
                        </span>
                        <span className={`badge ${selectedEp.has_final ? 'ok' : ''}`}>
                          {selectedEp.has_final ? 'Готовый mp4 ✓' : 'Ещё не собрано'}
                        </span>
                      </div>

                      <p className="text-sm text-muted mb-2">
                        Озвучку положи в папку эпизода как <code>voiceover.mp3</code> (ElevenLabs и т.п.).
                        После этого можно запускать рендер.
                      </p>

                      <div className="row mt-3" style={{ flexWrap: 'wrap' }}>
                        <Toggle on={preview} onChange={setPreview} label="Preview mode" />
                      </div>

                      <div className="row mt-3" style={{ flexWrap: 'wrap', gap: 8 }}>
                        <button
                          className="btn btn-success"
                          onClick={() => startRender(selectedEp)}
                          disabled={!selectedEp.has_scenes || !selectedEp.has_voice}
                        >
                          Собрать ролик
                        </button>
                        <button
                          className="btn btn-ghost"
                          onClick={() => startSheet(selectedEp)}
                          disabled={!selectedEp.has_voice}
                        >
                          Контактный лист
                        </button>
                        {selectedEp.has_final && (
                          <button
                            className="btn btn-primary"
                            onClick={() => download(`${selectedEp.path}/build/${selectedEp.final_name}`)}
                          >
                            Скачать MP4
                          </button>
                        )}
                        {selectedEp.has_meta && (
                          <button
                            className="btn btn-ghost"
                            onClick={() => download(`${selectedEp.path}/build/youtube_metadata.txt`)}
                          >
                            Метаданные
                          </button>
                        )}
                        {selectedEp.has_sheet && (
                          <button
                            className="btn btn-ghost"
                            onClick={() => download(`${selectedEp.path}/build/contact_sheet.png`)}
                          >
                            Sheet PNG
                          </button>
                        )}
                      </div>

                      <div className="mt-3 text-sm text-muted">
                        <div>Путь: <code>{selectedEp.path}</code></div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Status bar */}
        <div className="status-bar">
          <span>Jobs:</span>
          {recentJobs.length === 0 && <span className="text-muted">нет активных</span>}
          {recentJobs.map((j) => (
            <span key={j.id} className={`job-pill ${j.status}`}>
              {(j.status === 'running' || j.status === 'queued') && <span className="spinner" />}
              {j.id} — {j.status}
            </span>
          ))}
          <span className="ml-auto text-muted">localhost · React + FastAPI</span>
        </div>
      </div>

      {/* Modals */}
      {showNewChannel && (
        <Modal
          title="Новый канал"
          onClose={() => setShowNewChannel(false)}
          footer={
            <>
              <button className="btn btn-ghost" onClick={() => setShowNewChannel(false)}>
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleCreateChannel}>
                Создать
              </button>
            </>
          }
        >
          <div className="field">
            <label>Имя канала</label>
            <input
              value={newChannelName}
              onChange={(e) => setNewChannelName(e.target.value)}
              placeholder="например zuppy"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleCreateChannel()}
            />
          </div>
        </Modal>
      )}

      {showNewEpisode && (
        <Modal
          title="Новый эпизод"
          onClose={() => setShowNewEpisode(false)}
          footer={
            <>
              <button className="btn btn-ghost" onClick={() => setShowNewEpisode(false)}>
                Отмена
              </button>
              <button className="btn btn-primary" onClick={handleCreateEpisode}>
                Создать
              </button>
            </>
          }
        >
          <div className="field">
            <label>Тип</label>
            <select value={newEpKind} onChange={(e) => setNewEpKind(e.target.value)}>
              <option value="shorts">Shorts (вертикальный)</option>
              <option value="long">Long (горизонтальный)</option>
            </select>
          </div>
          <div className="field">
            <label>Короткое имя</label>
            <input
              value={newEpName}
              onChange={(e) => setNewEpName(e.target.value)}
              placeholder="например yawn_contagious"
              autoFocus
              onKeyDown={(e) => e.key === 'Enter' && handleCreateEpisode()}
            />
          </div>
        </Modal>
      )}
    </div>
  )
}
