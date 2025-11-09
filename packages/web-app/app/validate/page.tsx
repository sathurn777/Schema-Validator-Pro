"use client";

import { useState } from "react";
import { validateArticleSchema, validateProductSchema } from "@schema-validator-pro/core";
import type { ValidationResult } from "@schema-validator-pro/core";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";

export default function ValidatePage() {
  const [jsonInput, setJsonInput] = useState("");
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  const handleValidate = () => {
    try {
      const schema = JSON.parse(jsonInput);
      let result: ValidationResult;

      // Detect schema type and validate accordingly
      if (schema["@type"] === "Article") {
        result = validateArticleSchema(schema);
      } else if (schema["@type"] === "Product") {
        result = validateProductSchema(schema);
      } else {
        result = {
          valid: false,
          errors: [`Unsupported schema type: ${schema["@type"]}`],
          warnings: [],
        };
      }

      setValidationResult(result);
    } catch (error) {
      setValidationResult({
        valid: false,
        errors: ["Invalid JSON format"],
        warnings: [],
      });
    }
  };

  const handleClear = () => {
    setJsonInput("");
    setValidationResult(null);
  };

  return (
    <div className="container py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Validate Schema</h1>
          <p className="text-muted-foreground mt-2">
            Validate your Schema.org JSON-LD structured data
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Input Section */}
          <Card>
            <CardHeader>
              <CardTitle>JSON-LD Input</CardTitle>
              <CardDescription>Paste your Schema.org JSON-LD code</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="jsonInput">Schema JSON-LD</Label>
                <Textarea
                  id="jsonInput"
                  value={jsonInput}
                  onChange={(e) => setJsonInput(e.target.value)}
                  placeholder='{"@context": "https://schema.org", "@type": "Article", ...}'
                  className="min-h-[400px] font-mono text-sm"
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleValidate} className="flex-1">
                  Validate
                </Button>
                <Button onClick={handleClear} variant="outline" className="flex-1">
                  Clear
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results Section */}
          <Card>
            <CardHeader>
              <CardTitle>Validation Results</CardTitle>
              <CardDescription>See errors and warnings in your schema</CardDescription>
            </CardHeader>
            <CardContent>
              {validationResult ? (
                <div className="space-y-4">
                  {/* Status */}
                  <div className={`flex items-center gap-2 p-4 rounded-lg ${
                    validationResult.valid 
                      ? "bg-green-50 text-green-900 dark:bg-green-950 dark:text-green-100" 
                      : "bg-red-50 text-red-900 dark:bg-red-950 dark:text-red-100"
                  }`}>
                    {validationResult.valid ? (
                      <>
                        <CheckCircle2 className="h-5 w-5" />
                        <span className="font-semibold">Valid Schema</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-5 w-5" />
                        <span className="font-semibold">Invalid Schema</span>
                      </>
                    )}
                  </div>

                  {/* Errors */}
                  {validationResult.errors.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-500" />
                        Errors ({validationResult.errors.length})
                      </h3>
                      <ul className="space-y-1">
                        {validationResult.errors.map((error, index) => (
                          <li key={index} className="text-sm text-red-600 dark:text-red-400 pl-6">
                            • {error}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Warnings */}
                  {validationResult.warnings.length > 0 && (
                    <div className="space-y-2">
                      <h3 className="font-semibold flex items-center gap-2">
                        <AlertCircle className="h-4 w-4 text-yellow-500" />
                        Warnings ({validationResult.warnings.length})
                      </h3>
                      <ul className="space-y-1">
                        {validationResult.warnings.map((warning, index) => (
                          <li key={index} className="text-sm text-yellow-600 dark:text-yellow-400 pl-6">
                            • {warning}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Success message */}
                  {validationResult.valid && validationResult.errors.length === 0 && validationResult.warnings.length === 0 && (
                    <div className="text-center text-muted-foreground py-8">
                      <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-2" />
                      <p>Your schema is valid with no errors or warnings!</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-12">
                  Paste your JSON-LD and click validate to see results
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Example Section */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Example Schema</CardTitle>
            <CardDescription>Try validating this example Article schema</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="bg-muted p-4 rounded-lg overflow-auto text-sm">
              <code>{`{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Example Article Title",
  "author": {
    "@type": "Person",
    "name": "John Doe"
  },
  "datePublished": "2024-01-01",
  "description": "This is an example article description",
  "image": {
    "@type": "ImageObject",
    "url": "https://example.com/image.jpg"
  }
}`}</code>
            </pre>
            <Button 
              onClick={() => setJsonInput(`{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Example Article Title",
  "author": {
    "@type": "Person",
    "name": "John Doe"
  },
  "datePublished": "2024-01-01",
  "description": "This is an example article description",
  "image": {
    "@type": "ImageObject",
    "url": "https://example.com/image.jpg"
  }
}`)}
              variant="outline"
              className="mt-4"
            >
              Load Example
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

