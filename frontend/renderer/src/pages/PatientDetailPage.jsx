// src/pages/PatientDetailPage.jsx

import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useNotifications } from '../context/NotificationContext'

import PatientDetail    from '../components/PatientDetail'
import DemographicForm  from '../components/DemographicForm'
import Modal            from '../components/Modal'
import RecordingList    from '../components/RecordingList'

import { fetchPatient, fetchDemographics, fetchAssessments } from '../api/patient'
import { createAssessment }      from '../api/assessment'
import { uploadRecording }       from '../api/recording'

export default function PatientDetailPage() {
  const { id: patientId } = useParams()
  const navigate = useNavigate()
  const { addToast } = useNotifications()

  // --- state ---
  const [patient, setPatient]       = useState(null)
  const [demos, setDemos]           = useState([])
  const [assessments, setAssessments] = useState([])

  const [loadingDemo, setLoadingDemo]       = useState(true)
  const [loadingAsmts, setLoadingAsmts]     = useState(true)

  // audio-test form
  const [taskType, setTaskType]     = useState('')
  const [device, setDevice]         = useState('')
  const [file, setFile]             = useState(null)
  const [uploading, setUploading]   = useState(false)

  // --- load patient/data ---
  useEffect(() => {
    if (!patientId) return

    fetchPatient(patientId)
      .then(setPatient)
      .catch(() => addToast('Could not load patient', 'error'))

    setLoadingDemo(true)
    fetchDemographics(patientId)
      .then(setDemos)
      .catch(() => addToast('Could not load demographics', 'error'))
      .finally(() => setLoadingDemo(false))

    setLoadingAsmts(true)
    fetchAssessments(patientId)
      .then(setAssessments)
      .catch(() => addToast('Could not load assessments', 'error'))
      .finally(() => setLoadingAsmts(false))
  }, [patientId])

  // --- handlers ---
  const handleDemoSaved = () => addToast('Demographics saved', 'success')

  const handleAsmtSaved = () => {
    setLoadingAsmts(true)
    fetchAssessments(patientId)
      .then(arr => {
        setAssessments(arr)
        addToast('Assessment saved', 'success')
      })
      .catch(() => addToast('Could not reload assessments', 'error'))
      .finally(() => setLoadingAsmts(false))
  }

  async function handleAudioSubmit(e) {
    e.preventDefault()
    if (!taskType || !file) return addToast('Fill every field', 'error')
    setUploading(true)

    try {
      // 1) Create a new “dummy” assessment of type = taskType so we get an assessment_id
      const newAsm = await createAssessment(patientId, {
        assessment_type: taskType,
        score: 0,
        max_possible_score: null,
        assessment_date: new Date().toISOString(),
        diagnosis: null,
        notes: null,
        subscores: [],
      })

      // 2) upload the audio to that assessment
      const form = new FormData()
      form.append('file', file)
      // you can pass device/task_type via metadata or extend your uploadRecording fn
      form.append('recording_device', device)
      form.append('task_type', taskType)

      const rec = await uploadRecording(
        patientId,
        newAsm.assessment_id,
        form
      )

      addToast('Audio test uploaded', 'success')
      // optionally push into a RecordingList if you render one…
      setTaskType('')
      setDevice('')
      setFile(null)
    } catch (err) {
      console.error(err)
      addToast('Upload failed', 'error')
    } finally {
      setUploading(false)
      // reload the assessments list so your new one appears
      handleAsmtSaved()
    }
  }

  if (!patient) return <div>Loading patient…</div>

  return (
    <div className="container mx-auto p-4 space-y-8">
      <button
        onClick={() => navigate(-1)}
        className="px-3 py-1 bg-gray-200 rounded"
      >
        ← Back
      </button>

      <h2 className="text-2xl font-semibold">Patient Details</h2>
      <PatientDetail patientId={patientId} onSuccess={() => addToast('Patient saved','success')} />

      <section>
        <h3 className="text-xl font-medium mb-2">Demographics</h3>
        {loadingDemo
          ? <div>Loading…</div>
          : <DemographicForm
              patientId={patientId}
              initialData={demos[0] ?? null}
              onSaved={handleDemoSaved}
            />
        }
      </section>

      <section>
        <h3 className="text-xl font-medium mb-2">Cognitive Assessments</h3>
        {/* …your existing assessments form and table… */}
      </section>

      {/* ——————————————— */}
      {/* NEW: Audio-Based Tests */}
      <section>
        <h3 className="text-xl font-medium mb-2">Audio-Based Tests</h3>

        <form onSubmit={handleAudioSubmit} className="border p-4 rounded mb-4">
          <div className="mb-2">
            <label className="block font-medium">Test Name</label>
            <input
              type="text"
              value={taskType}
              onChange={e => setTaskType(e.target.value)}
              className="mt-1 block w-full border rounded px-2 py-1"
              placeholder="e.g. Cookie Theft"
              required
            />
          </div>
          <div className="mb-2">
            <label className="block font-medium">Recording Device</label>
            <input
              type="text"
              value={device}
              onChange={e => setDevice(e.target.value)}
              className="mt-1 block w-full border rounded px-2 py-1"
              placeholder="e.g. Zoom, Phone"
            />
          </div>
          <div className="mb-2">
            <label className="block font-medium">Audio File</label>
            <input
              type="file"
              accept="audio/*"
              onChange={e => setFile(e.target.files[0])}
              className="mt-1 block w-full"
              required
            />
          </div>
          <button
            type="submit"
            disabled={uploading}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            {uploading ? 'Uploading…' : 'Upload Audio Test'}
          </button>
        </form>
      </section>
    </div>
  )
}
