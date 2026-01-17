import { useState, useEffect, useRef } from 'react'
import WaveSurfer from 'wavesurfer.js'

const API_BASE = 'http://localhost:8000'

const STATUSES = {
  idea: { label: 'Idea', color: 'bg-blue-500' },
  exported: { label: 'Exported', color: 'bg-yellow-500' },
  packaged: { label: 'Packaged', color: 'bg-orange-500' },
  released: { label: 'Released', color: 'bg-green-500' }
}

function ProjectCard({ project, onPlay, isPlaying, onStatusChange, onUploadToSoundCloud, isUploading, onUploadCover, onUploadAudio }) {
  const coverUrl = project.cover_url ? `${API_BASE}${project.cover_url}` : null
  const hasAudio = project.preview_url && project.audio_clips > 0
  const coverInputRef = useRef(null)
  const audioInputRef = useRef(null)

  const handleCoverUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onUploadCover(project.id, file)
    }
  }

  const handleAudioUpload = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      onUploadAudio(project.id, file)
    }
  }

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-indigo-500 transition-all">
      {/* Cover / Waveform */}
      <div
        className={`aspect-square bg-gray-700 relative group ${hasAudio ? 'cursor-pointer' : ''}`}
        onClick={() => hasAudio && onPlay(project)}
      >
        {coverUrl ? (
          <img src={coverUrl} alt={project.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-6xl">
            🎵
          </div>
        )}

        {/* Play button overlay */}
        {hasAudio ? (
          <div className="absolute inset-0 bg-black bg-opacity-30 group-hover:bg-opacity-50 flex items-center justify-center transition-all">
            <div className="opacity-100 transition-opacity">
              {isPlaying ? (
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-3xl">⏸</span>
                </div>
              ) : (
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-3xl ml-1">▶</span>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-red-900 bg-opacity-80 text-white text-xs px-3 py-2 rounded text-center max-w-[80%]">
              No audio files found
            </div>
          </div>
        )}

        {/* Upload buttons - bottom left */}
        <div className="absolute bottom-2 left-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => {
              e.stopPropagation()
              coverInputRef.current?.click()
            }}
            className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs px-2 py-1 rounded"
            title="Upload cover art"
          >
            📷 Cover
          </button>
          {!hasAudio && (
            <button
              onClick={(e) => {
                e.stopPropagation()
                audioInputRef.current?.click()
              }}
              className="bg-green-600 hover:bg-green-700 text-white text-xs px-2 py-1 rounded"
              title="Upload audio file"
            >
              🎵 Audio
            </button>
          )}
        </div>
        <input
          ref={coverInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png,image/webp"
          onChange={handleCoverUpload}
          className="hidden"
        />
        <input
          ref={audioInputRef}
          type="file"
          accept="audio/mpeg,audio/mp3,audio/wav"
          onChange={handleAudioUpload}
          className="hidden"
        />

        {/* Status badge */}
        <div className={`absolute top-2 right-2 ${STATUSES[project.status].color} text-white text-xs px-2 py-1 rounded-full`}>
          {STATUSES[project.status].label}
        </div>

        {/* SoundCloud badge if uploaded */}
        {project.soundcloud_url && (
          <a
            href={project.soundcloud_url}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute top-2 left-2 bg-orange-500 text-white text-xs px-2 py-1 rounded-full hover:bg-orange-600"
            onClick={(e) => e.stopPropagation()}
          >
            🔊 On SoundCloud
          </a>
        )}
      </div>

      {/* Info */}
      <div className="p-4">
        <h3 className="text-white font-semibold mb-1 truncate" title={project.name}>
          {project.name}
        </h3>
        <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
          {project.bpm && <span>{project.bpm} BPM</span>}
          {project.key && <span>• {project.key}</span>}
        </div>

        {project.genre && (
          <div className="text-xs text-gray-500 mb-2">
            {project.genre}
          </div>
        )}

        {!hasAudio && project.audio_clips === 0 && (
          <div className="text-xs text-yellow-500 mb-2">
            ⚠️ Audio files not found - check project location
          </div>
        )}

        {/* Upload to SoundCloud button */}
        {hasAudio && !project.soundcloud_url && (
          <button
            onClick={() => onUploadToSoundCloud(project.id)}
            disabled={isUploading}
            className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white text-xs py-2 px-3 rounded mb-2 transition-colors"
          >
            {isUploading ? 'Uploading...' : '🔊 Upload to SoundCloud'}
          </button>
        )}

        {/* Status progression buttons */}
        <div className="flex gap-1 mt-3">
          {Object.keys(STATUSES).map(status => (
            <button
              key={status}
              onClick={() => onStatusChange(project.id, status)}
              className={`flex-1 h-1 rounded transition-all ${
                project.status === status
                  ? STATUSES[status].color
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
              title={STATUSES[status].label}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

function App() {
  const [projects, setProjects] = useState([])
  const [filteredProjects, setFilteredProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null)
  const [soundcloudConnected, setSoundcloudConnected] = useState(false)
  const [soundcloudUser, setSoundcloudUser] = useState(null)
  const [uploadingProject, setUploadingProject] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)

  // Filters
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [bpmRange, setBpmRange] = useState({ min: '', max: '' })

  const wavesurferRef = useRef(null)
  const waveformContainerRef = useRef(null)

  useEffect(() => {
    loadProjects()
    checkSoundCloudStatus()

    // Check for OAuth callback
    const params = new URLSearchParams(window.location.search)
    if (params.get('soundcloud') === 'connected') {
      alert('SoundCloud connected successfully!')
      checkSoundCloudStatus()
      window.history.replaceState({}, '', '/')
    } else if (params.get('soundcloud') === 'error') {
      alert(`SoundCloud connection error: ${params.get('message')}`)
      window.history.replaceState({}, '', '/')
    }
  }, [])

  useEffect(() => {
    applyFilters()
  }, [projects, statusFilter, searchQuery, bpmRange])

  const loadProjects = async () => {
    try {
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.append('status', statusFilter)
      if (searchQuery) params.append('search', searchQuery)
      if (bpmRange.min) params.append('min_bpm', bpmRange.min)
      if (bpmRange.max) params.append('max_bpm', bpmRange.max)

      const res = await fetch(`${API_BASE}/projects?${params}`)
      const data = await res.json()
      setProjects(data)
      setLoading(false)
    } catch (err) {
      console.error('Error fetching projects:', err)
      setLoading(false)
    }
  }

  const scanProjects = async () => {
    setScanning(true)
    try {
      const res = await fetch(`${API_BASE}/projects/scan`, { method: 'POST' })
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`)
      }
      const data = await res.json()
      alert(data.message)
      await loadProjects()
    } catch (err) {
      console.error('Error scanning projects:', err)
      alert(`Error scanning projects: ${err.message}`)
    } finally {
      setScanning(false)
    }
  }

  const applyFilters = () => {
    let filtered = [...projects]

    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => p.status === statusFilter)
    }

    if (searchQuery) {
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (bpmRange.min) {
      filtered = filtered.filter(p => p.bpm >= parseInt(bpmRange.min))
    }

    if (bpmRange.max) {
      filtered = filtered.filter(p => p.bpm <= parseInt(bpmRange.max))
    }

    setFilteredProjects(filtered)
  }

  const playPreview = (project) => {
    if (!project.preview_url) return

    // Stop if same project
    if (currentlyPlaying?.id === project.id) {
      wavesurferRef.current?.playPause()
      setIsPlaying(!isPlaying)
      return
    }

    // Destroy existing wavesurfer
    if (wavesurferRef.current) {
      wavesurferRef.current.destroy()
      wavesurferRef.current = null
    }

    // Set the project first - this will render the container
    setCurrentlyPlaying(project)
  }

  // Create WaveSurfer when currentlyPlaying changes
  useEffect(() => {
    if (!currentlyPlaying || !currentlyPlaying.preview_url) return

    // Wait for container to be available
    const initWaveSurfer = () => {
      if (!waveformContainerRef.current) {
        // Container not ready yet, try again
        setTimeout(initWaveSurfer, 50)
        return
      }

      // Create new wavesurfer
      const ws = WaveSurfer.create({
        container: waveformContainerRef.current,
        waveColor: '#6366f1',
        progressColor: '#4f46e5',
        cursorColor: '#818cf8',
        barWidth: 2,
        barRadius: 3,
        height: 80,
        normalize: true
      })

      ws.load(`${API_BASE}${currentlyPlaying.preview_url}`)
      ws.on('ready', () => {
        ws.play()
        setIsPlaying(true)
      })
      ws.on('finish', () => {
        setCurrentlyPlaying(null)
        setIsPlaying(false)
      })
      ws.on('pause', () => setIsPlaying(false))
      ws.on('play', () => setIsPlaying(true))

      wavesurferRef.current = ws
    }

    initWaveSurfer()

    // Cleanup
    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy()
        wavesurferRef.current = null
      }
    }
  }, [currentlyPlaying])

  const updateProjectStatus = async (projectId, newStatus) => {
    try {
      await fetch(`${API_BASE}/projects/${projectId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `status=${newStatus}`
      })

      // Update local state
      setProjects(projects.map(p =>
        p.id === projectId ? { ...p, status: newStatus } : p
      ))
    } catch (err) {
      console.error('Error updating project:', err)
    }
  }

  const checkSoundCloudStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/soundcloud/status`)
      const data = await res.json()
      setSoundcloudConnected(data.connected)
      setSoundcloudUser(data.user)
    } catch (err) {
      console.error('Error checking SoundCloud status:', err)
    }
  }

  const connectSoundCloud = async () => {
    try {
      const res = await fetch(`${API_BASE}/soundcloud/connect`)
      const data = await res.json()
      window.location.href = data.auth_url
    } catch (err) {
      console.error('Error connecting to SoundCloud:', err)
      alert('Error connecting to SoundCloud')
    }
  }

  const disconnectSoundCloud = async () => {
    if (!confirm('Disconnect from SoundCloud?')) return

    try {
      await fetch(`${API_BASE}/soundcloud/disconnect`, { method: 'POST' })
      setSoundcloudConnected(false)
      setSoundcloudUser(null)
      alert('Disconnected from SoundCloud')
    } catch (err) {
      console.error('Error disconnecting:', err)
    }
  }

  const uploadToSoundCloud = async (projectId) => {
    if (!soundcloudConnected) {
      if (confirm('Connect to SoundCloud to upload tracks?')) {
        connectSoundCloud()
      }
      return
    }

    setUploadingProject(projectId)

    try {
      const res = await fetch(`${API_BASE}/projects/${projectId}/upload-soundcloud`, {
        method: 'POST'
      })

      if (res.status === 401) {
        alert('Please connect your SoundCloud account first')
        return
      }

      if (res.status === 400) {
        const data = await res.json()
        alert(data.detail)
        return
      }

      const data = await res.json()
      alert(`Upload started! Check back in a few moments. ${data.message}`)

      // Reload projects after a delay to show updated status
      setTimeout(() => {
        loadProjects()
        setUploadingProject(null)
      }, 5000)

    } catch (err) {
      console.error('Error uploading to SoundCloud:', err)
      alert('Error uploading to SoundCloud')
      setUploadingProject(null)
    }
  }

  const uploadCover = async (projectId, file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE}/projects/${projectId}/cover`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const data = await res.json()
      alert(data.message)
      await loadProjects()
    } catch (err) {
      console.error('Error uploading cover:', err)
      alert(`Failed to upload cover: ${err.message}`)
    }
  }

  const uploadAudio = async (projectId, file) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE}/projects/${projectId}/audio`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Upload failed')
      }

      const data = await res.json()
      alert(data.message)
      await loadProjects()
    } catch (err) {
      console.error('Error uploading audio:', err)
      alert(`Failed to upload audio: ${err.message}`)
    }
  }

  const createProject = async (formData) => {
    setCreating(true)
    try {
      const res = await fetch(`${API_BASE}/projects/create`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const error = await res.json()
        throw new Error(error.detail || 'Create failed')
      }

      const data = await res.json()
      alert(data.message)
      setShowCreateModal(false)
      await loadProjects()
    } catch (err) {
      console.error('Error creating project:', err)
      alert(`Failed to create project: ${err.message}`)
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading Release OS...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">Release OS</h1>
              <p className="text-gray-400 mt-1">
                {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''}
                {filteredProjects.length !== projects.length && ` (filtered from ${projects.length})`}
              </p>
            </div>
            <div className="flex gap-3">
              {soundcloudConnected ? (
                <div className="flex items-center gap-2">
                  <div className="text-sm text-gray-300">
                    🔊 {soundcloudUser?.username || 'Connected'}
                  </div>
                  <button
                    onClick={disconnectSoundCloud}
                    className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-3 rounded-lg text-sm transition-colors"
                  >
                    Disconnect
                  </button>
                </div>
              ) : (
                <button
                  onClick={connectSoundCloud}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  🔊 Connect SoundCloud
                </button>
              )}
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                + New Project
              </button>
              <button
                onClick={scanProjects}
                disabled={scanning}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                {scanning ? 'Scanning...' : 'Scan Projects'}
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-4 items-center">
            {/* Status filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              {Object.entries(STATUSES).map(([key, { label }]) => (
                <option key={key} value={key}>{label}</option>
              ))}
            </select>

            {/* Search */}
            <input
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-1 max-w-md"
            />

            {/* BPM range */}
            <div className="flex items-center gap-2">
              <input
                type="number"
                placeholder="Min BPM"
                value={bpmRange.min}
                onChange={(e) => setBpmRange({ ...bpmRange, min: e.target.value })}
                className="bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-24"
              />
              <span className="text-gray-400">-</span>
              <input
                type="number"
                placeholder="Max BPM"
                value={bpmRange.max}
                onChange={(e) => setBpmRange({ ...bpmRange, max: e.target.value })}
                className="bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 w-24"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* Audio player */}
        {currentlyPlaying && (
          <div className="bg-gray-800 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-white font-semibold text-lg">{currentlyPlaying.name}</h3>
                <p className="text-gray-400 text-sm">{currentlyPlaying.bpm} BPM • {currentlyPlaying.key || 'No key'}</p>
              </div>
              <div className="flex items-center gap-3">
                {/* Play/Pause button */}
                <button
                  onClick={() => wavesurferRef.current?.playPause()}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full w-12 h-12 flex items-center justify-center transition-colors"
                  title={isPlaying ? 'Pause' : 'Play'}
                >
                  {isPlaying ? (
                    <span className="text-2xl">⏸</span>
                  ) : (
                    <span className="text-2xl ml-1">▶</span>
                  )}
                </button>

                {/* Stop button */}
                <button
                  onClick={() => {
                    wavesurferRef.current?.stop()
                    setIsPlaying(false)
                  }}
                  className="bg-gray-700 hover:bg-gray-600 text-white rounded-full w-10 h-10 flex items-center justify-center transition-colors"
                  title="Stop"
                >
                  <span className="text-xl">⏹</span>
                </button>

                {/* Replay button */}
                <button
                  onClick={() => {
                    wavesurferRef.current?.seekTo(0)
                    wavesurferRef.current?.play()
                    setIsPlaying(true)
                  }}
                  className="bg-gray-700 hover:bg-gray-600 text-white rounded-full w-10 h-10 flex items-center justify-center transition-colors"
                  title="Replay from start"
                >
                  <span className="text-xl">↻</span>
                </button>

                {/* Close button */}
                <button
                  onClick={() => {
                    wavesurferRef.current?.destroy()
                    setCurrentlyPlaying(null)
                    setIsPlaying(false)
                  }}
                  className="text-gray-400 hover:text-white text-2xl"
                  title="Close player"
                >
                  ✕
                </button>
              </div>
            </div>
            <div ref={waveformContainerRef} className="rounded overflow-hidden" />
          </div>
        )}

        {/* Projects grid */}
        {filteredProjects.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-6xl mb-4">🎵</div>
            <p className="text-gray-400 text-lg mb-2">No projects found</p>
            <p className="text-gray-500 text-sm mb-6">
              Drop your Ableton projects in ~/Music/ReleaseDrop
            </p>
            <button
              onClick={scanProjects}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium"
            >
              Scan for Projects
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredProjects.map(project => (
              <ProjectCard
                key={project.id}
                project={project}
                onPlay={playPreview}
                isPlaying={currentlyPlaying?.id === project.id}
                onStatusChange={updateProjectStatus}
                onUploadToSoundCloud={uploadToSoundCloud}
                isUploading={uploadingProject === project.id}
                onUploadCover={uploadCover}
                onUploadAudio={uploadAudio}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold text-white mb-4">Create New Project</h2>
            <form onSubmit={(e) => {
              e.preventDefault()
              const formData = new FormData(e.target)
              createProject(formData)
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Project Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    required
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="My Awesome Track"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Audio File (MP3/WAV) *
                  </label>
                  <input
                    type="file"
                    name="file"
                    accept="audio/mpeg,audio/mp3,audio/wav"
                    required
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      BPM
                    </label>
                    <input
                      type="number"
                      name="bpm"
                      className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="120"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Key
                    </label>
                    <input
                      type="text"
                      name="key"
                      className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="C minor"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">
                    Genre
                  </label>
                  <input
                    type="text"
                    name="genre"
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="House, Techno, etc."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  {creating ? 'Creating...' : 'Create Project'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default App