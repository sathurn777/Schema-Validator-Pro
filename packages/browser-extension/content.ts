import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  all_frames: false
}

// Detect Schema.org JSON-LD on the page
function detectSchemas() {
  const schemas: any[] = []
  
  // Find all script tags with type="application/ld+json"
  const scriptTags = document.querySelectorAll('script[type="application/ld+json"]')
  
  scriptTags.forEach((script, index) => {
    try {
      const jsonContent = script.textContent || ""
      const schemaData = JSON.parse(jsonContent)
      
      schemas.push({
        index,
        type: schemaData["@type"] || "Unknown",
        data: schemaData,
        element: script
      })
    } catch (error) {
      console.error("Failed to parse schema:", error)
    }
  })
  
  return schemas
}

// Highlight schema elements on the page
function highlightSchemas(schemas: any[]) {
  schemas.forEach((schema) => {
    if (schema.element) {
      // Add a visual indicator next to the schema
      const indicator = document.createElement("div")
      indicator.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        background: #4CAF50;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      `
      indicator.textContent = `Schema.org ${schema.type} detected`
      document.body.appendChild(indicator)
      
      // Remove after 3 seconds
      setTimeout(() => {
        indicator.remove()
      }, 3000)
    }
  })
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "detectSchemas") {
    const schemas = detectSchemas()
    sendResponse({ schemas })
  } else if (request.action === "highlightSchemas") {
    const schemas = detectSchemas()
    highlightSchemas(schemas)
    sendResponse({ success: true })
  }
  return true
})

// Auto-detect on page load
window.addEventListener("load", () => {
  const schemas = detectSchemas()
  
  if (schemas.length > 0) {
    // Send to background script
    chrome.runtime.sendMessage({
      action: "schemasDetected",
      count: schemas.length,
      schemas: schemas.map(s => ({
        type: s.type,
        data: s.data
      }))
    })
  }
})

console.log("Schema Validator Pro: Content script loaded")

