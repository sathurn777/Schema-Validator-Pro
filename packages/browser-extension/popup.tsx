import { useEffect, useState } from "react"
import type { ValidationResult } from "@schema-validator-pro/core"

import "./popup.css"

interface DetectedSchema {
  type: string
  data: any
  validation?: ValidationResult
}

function IndexPopup() {
  const [schemas, setSchemas] = useState<DetectedSchema[]>([])
  const [loading, setLoading] = useState(true)
  const [validating, setValidating] = useState(false)

  useEffect(() => {
    loadSchemas()
  }, [])

  const loadSchemas = async () => {
    setLoading(true)
    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })

      if (tab.id) {
        // Inject content script if not already injected
        try {
          await chrome.tabs.sendMessage(tab.id, { action: "ping" })
        } catch {
          await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ["content.ts"]
          })
        }

        // Get schemas from content script
        const response = await chrome.tabs.sendMessage(tab.id, { action: "detectSchemas" })
        setSchemas(response.schemas || [])
      }
    } catch (error) {
      console.error("Failed to load schemas:", error)
    } finally {
      setLoading(false)
    }
  }

  const validateAllSchemas = async () => {
    setValidating(true)
    try {
      const response = await chrome.runtime.sendMessage({ action: "validateAllSchemas" })

      if (response.results) {
        setSchemas(prevSchemas =>
          prevSchemas.map((schema, index) => ({
            ...schema,
            validation: response.results[index]?.validation
          }))
        )
      }
    } catch (error) {
      console.error("Failed to validate schemas:", error)
    } finally {
      setValidating(false)
    }
  }

  const highlightSchemas = async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
      if (tab.id) {
        await chrome.tabs.sendMessage(tab.id, { action: "highlightSchemas" })
      }
    } catch (error) {
      console.error("Failed to highlight schemas:", error)
    }
  }

  return (
    <div className="popup-container">
      <div className="popup-header">
        <h1>Schema Validator Pro</h1>
        <p className="subtitle">Detect and validate Schema.org JSON-LD</p>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : schemas.length === 0 ? (
        <div className="empty-state">
          <p>No Schema.org JSON-LD found on this page</p>
        </div>
      ) : (
        <>
          <div className="stats">
            <div className="stat-item">
              <span className="stat-value">{schemas.length}</span>
              <span className="stat-label">Schemas Found</span>
            </div>
          </div>

          <div className="actions">
            <button onClick={validateAllSchemas} disabled={validating} className="btn btn-primary">
              {validating ? "Validating..." : "Validate All"}
            </button>
            <button onClick={highlightSchemas} className="btn btn-secondary">
              Highlight
            </button>
          </div>

          <div className="schemas-list">
            {schemas.map((schema, index) => (
              <div key={index} className="schema-item">
                <div className="schema-header">
                  <span className="schema-type">{schema.type}</span>
                  {schema.validation && (
                    <span className={`schema-status ${schema.validation.valid ? "valid" : "invalid"}`}>
                      {schema.validation.valid ? "✓ Valid" : "✗ Invalid"}
                    </span>
                  )}
                </div>

                {schema.validation && (
                  <div className="validation-details">
                    {schema.validation.errors.length > 0 && (
                      <div className="errors">
                        <strong>Errors:</strong>
                        <ul>
                          {schema.validation.errors.map((error, i) => (
                            <li key={i}>{error}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {schema.validation.warnings.length > 0 && (
                      <div className="warnings">
                        <strong>Warnings:</strong>
                        <ul>
                          {schema.validation.warnings.map((warning, i) => (
                            <li key={i}>{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default IndexPopup
