import { useEffect, useState } from "react"

import "./options.css"

interface Settings {
  autoDetect: boolean
  showNotifications: boolean
  highlightOnLoad: boolean
}

function OptionsPage() {
  const [settings, setSettings] = useState<Settings>({
    autoDetect: true,
    showNotifications: true,
    highlightOnLoad: false
  })
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const result = await chrome.storage.sync.get("settings")
      if (result.settings) {
        setSettings(result.settings)
      }
    } catch (error) {
      console.error("Failed to load settings:", error)
    }
  }

  const saveSettings = async () => {
    try {
      await chrome.storage.sync.set({ settings })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (error) {
      console.error("Failed to save settings:", error)
    }
  }

  const handleChange = (key: keyof Settings) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }))
  }

  return (
    <div className="options-container">
      <div className="options-header">
        <h1>Schema Validator Pro Settings</h1>
        <p className="subtitle">Configure your extension preferences</p>
      </div>

      <div className="options-content">
        <div className="settings-section">
          <h2>Detection Settings</h2>
          
          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="autoDetect">Auto-detect schemas</label>
              <p className="setting-description">
                Automatically detect Schema.org JSON-LD when a page loads
              </p>
            </div>
            <input
              type="checkbox"
              id="autoDetect"
              checked={settings.autoDetect}
              onChange={() => handleChange("autoDetect")}
              className="toggle"
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="showNotifications">Show notifications</label>
              <p className="setting-description">
                Display a notification when schemas are detected
              </p>
            </div>
            <input
              type="checkbox"
              id="showNotifications"
              checked={settings.showNotifications}
              onChange={() => handleChange("showNotifications")}
              className="toggle"
            />
          </div>

          <div className="setting-item">
            <div className="setting-info">
              <label htmlFor="highlightOnLoad">Highlight on page load</label>
              <p className="setting-description">
                Automatically highlight detected schemas when page loads
              </p>
            </div>
            <input
              type="checkbox"
              id="highlightOnLoad"
              checked={settings.highlightOnLoad}
              onChange={() => handleChange("highlightOnLoad")}
              className="toggle"
            />
          </div>
        </div>

        <div className="settings-section">
          <h2>About</h2>
          <div className="about-info">
            <p><strong>Version:</strong> 0.1.0</p>
            <p><strong>Author:</strong> Schema Validator Pro Team</p>
            <p className="description">
              Schema Validator Pro helps you detect and validate Schema.org JSON-LD structured data
              on web pages. It supports Article, Product, Recipe, Event, and more schema types.
            </p>
          </div>
        </div>

        <div className="actions">
          <button onClick={saveSettings} className="btn btn-primary">
            {saved ? "✓ Saved!" : "Save Settings"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default OptionsPage

