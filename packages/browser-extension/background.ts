import { validateArticleSchema, validateProductSchema } from "@schema-validator-pro/core"
import type { ValidationResult } from "@schema-validator-pro/core"

// Store detected schemas
const detectedSchemas = new Map<number, any[]>()

// Validate a schema based on its type
function validateSchema(schema: any): ValidationResult {
  const schemaType = schema["@type"]
  
  switch (schemaType) {
    case "Article":
      return validateArticleSchema(schema)
    case "Product":
      return validateProductSchema(schema)
    default:
      return {
        valid: false,
        errors: [`Unsupported schema type: ${schemaType}`],
        warnings: []
      }
  }
}

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "schemasDetected") {
    // Store schemas for this tab
    if (sender.tab?.id) {
      detectedSchemas.set(sender.tab.id, request.schemas)
      
      // Update badge
      chrome.action.setBadgeText({
        text: request.count.toString(),
        tabId: sender.tab.id
      })
      
      chrome.action.setBadgeBackgroundColor({
        color: "#4CAF50",
        tabId: sender.tab.id
      })
    }
    
    sendResponse({ success: true })
  } else if (request.action === "getSchemas") {
    // Return schemas for current tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0]?.id
      if (tabId) {
        const schemas = detectedSchemas.get(tabId) || []
        sendResponse({ schemas })
      } else {
        sendResponse({ schemas: [] })
      }
    })
    return true // Keep channel open for async response
  } else if (request.action === "validateSchema") {
    // Validate a specific schema
    const result = validateSchema(request.schema)
    sendResponse({ result })
  } else if (request.action === "validateAllSchemas") {
    // Validate all schemas for current tab
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0]?.id
      if (tabId) {
        const schemas = detectedSchemas.get(tabId) || []
        const results = schemas.map(s => ({
          type: s.type,
          validation: validateSchema(s.data)
        }))
        sendResponse({ results })
      } else {
        sendResponse({ results: [] })
      }
    })
    return true // Keep channel open for async response
  }
  
  return true
})

// Clear badge when tab is closed
chrome.tabs.onRemoved.addListener((tabId) => {
  detectedSchemas.delete(tabId)
})

// Clear badge when navigating to a new page
chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "loading") {
    detectedSchemas.delete(tabId)
    chrome.action.setBadgeText({ text: "", tabId })
  }
})

console.log("Schema Validator Pro: Background script loaded")

