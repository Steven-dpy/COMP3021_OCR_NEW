import React, { useState, useRef } from 'react'
import './App.css'

function App() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [serialNumber, setSerialNumber] = useState('')
  const [confidence, setConfidence] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [images, setImages] = useState(null)
  const [startTime, setStartTime] = useState(null)
  const [processingTime, setProcessingTime] = useState(0)
  const timerIntervalRef = useRef(null)

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
    setError('')
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image file first')
      return
    }

    setLoading(true)
    setError('')
    setImages(null)

    // count time
    const start = new Date()
    setStartTime(start)
    setProcessingTime(0)
    const interval = setInterval(() => {
      const currentTime = new Date()
      const elapsedSeconds = Math.floor((currentTime - start) / 1000)
      setProcessingTime(elapsedSeconds)
    }, 1000)
    timerIntervalRef.current = interval

    try {
      const formData = new FormData()
      formData.append('image', selectedFile)

      const response = await fetch('/api/upload/', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      setSerialNumber(data.serial_number)
      setConfidence(data.confidence)
      setImages({
        origin_image: data.origin_image,
        cropped_image: data.cropped_image,
        stretched_image: data.stretched_image,
        processed_image: data.processed_image,
        ocr_image: data.ocr_image,
      })
    } catch (err) {
      setError('An error occurred during recognition. Please try again.')
      console.error('Error:', err)
    } finally {
      clearInterval(timerIntervalRef.current)
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Blue Part Serial Number Recognition</h1>

        <div className="upload-container">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="file-input"
          />

          <button
            onClick={handleUpload}
            disabled={loading || !selectedFile}
            className="upload-button"
          >
            {loading ? 'Processing...' : 'Recognize Serial Number'}
          </button>
        </div>
        <div className="results-section">
          {loading && (
            <div className="loading-state">
              <p>Recognizing... {processingTime}s</p>
            </div>
          )}

          {error && <div className="error-message">{error}</div>}

          {!loading && serialNumber && (
            <div className="result-container">
              <h2>Recognition Result</h2>
              <p>
                <strong>Processing Time:</strong> {processingTime}s
              </p>
              <p>
                <strong>Serial Number:</strong> {serialNumber}
              </p>
              <p>
                <strong>Confidence:</strong> {Math.round(confidence * 100)}%
              </p>

              {images && (
                <div className="images-container">
                  <h3>Processed Images</h3>
                  <div className="image-grid">
                    <div className="image-item">
                      <img
                        src={`http://localhost:8081/share/${images.origin_image}`}
                        alt="Original Image"
                      />
                      <p>Original</p>
                    </div>
                    <div className="image-item">
                      <img
                        src={`http://localhost:8081/share/${images.cropped_image}`}
                        alt="Cropped Image"
                      />
                      <p>Cropped</p>
                    </div>
                    <div className="image-item">
                      <img
                        src={`http://localhost:8081/share/${images.stretched_image}`}
                        alt="Stretched Image"
                      />
                      <p>Stretched</p>
                    </div>
                    <div className="image-item">
                      <img
                        src={`http://localhost:8081/share/${images.processed_image}`}
                        alt="Processed Image"
                      />
                      <p>Processed</p>
                    </div>
                    <div className="image-item">
                      <img
                        src={`http://localhost:8081/share/${images.ocr_image}`}
                        alt="OCR Image"
                      />
                      <p>OCR Result</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </header>
    </div>
  )
}

export default App
