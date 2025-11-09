"use client";

import { useState } from "react";
import { generateArticleSchema, generateProductSchema } from "@schema-validator-pro/core";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Copy, Download } from "lucide-react";

type SchemaType = "Article" | "Product";

export default function GeneratePage() {
  const [schemaType, setSchemaType] = useState<SchemaType>("Article");
  const [generatedSchema, setGeneratedSchema] = useState<string>("");
  
  // Article form state
  const [articleData, setArticleData] = useState({
    headline: "",
    author: "",
    datePublished: "",
    description: "",
    imageUrl: "",
  });

  // Product form state
  const [productData, setProductData] = useState({
    name: "",
    description: "",
    imageUrl: "",
    price: "",
    currency: "USD",
  });

  const handleGenerateArticle = () => {
    const schema = generateArticleSchema({
      headline: articleData.headline,
      author: {
        "@type": "Person",
        name: articleData.author,
      },
      datePublished: articleData.datePublished,
      description: articleData.description,
      image: articleData.imageUrl ? {
        "@type": "ImageObject",
        url: articleData.imageUrl,
      } : undefined,
    });
    setGeneratedSchema(JSON.stringify(schema, null, 2));
  };

  const handleGenerateProduct = () => {
    const schema = generateProductSchema({
      name: productData.name,
      description: productData.description,
      image: productData.imageUrl ? {
        "@type": "ImageObject",
        url: productData.imageUrl,
      } : undefined,
      offers: {
        "@type": "Offer",
        price: productData.price,
        priceCurrency: productData.currency,
      },
    });
    setGeneratedSchema(JSON.stringify(schema, null, 2));
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedSchema);
  };

  const handleDownload = () => {
    const blob = new Blob([generatedSchema], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${schemaType.toLowerCase()}-schema.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Generate Schema</h1>
          <p className="text-muted-foreground mt-2">
            Create valid Schema.org JSON-LD structured data
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Form Section */}
          <Card>
            <CardHeader>
              <CardTitle>Schema Type</CardTitle>
              <CardDescription>Select a schema type and fill in the details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button
                  variant={schemaType === "Article" ? "default" : "outline"}
                  onClick={() => setSchemaType("Article")}
                >
                  Article
                </Button>
                <Button
                  variant={schemaType === "Product" ? "default" : "outline"}
                  onClick={() => setSchemaType("Product")}
                >
                  Product
                </Button>
              </div>

              {schemaType === "Article" && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="headline">Headline *</Label>
                    <Input
                      id="headline"
                      value={articleData.headline}
                      onChange={(e) => setArticleData({ ...articleData, headline: e.target.value })}
                      placeholder="Enter article headline"
                    />
                  </div>
                  <div>
                    <Label htmlFor="author">Author *</Label>
                    <Input
                      id="author"
                      value={articleData.author}
                      onChange={(e) => setArticleData({ ...articleData, author: e.target.value })}
                      placeholder="Enter author name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="datePublished">Date Published</Label>
                    <Input
                      id="datePublished"
                      type="date"
                      value={articleData.datePublished}
                      onChange={(e) => setArticleData({ ...articleData, datePublished: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={articleData.description}
                      onChange={(e) => setArticleData({ ...articleData, description: e.target.value })}
                      placeholder="Enter article description"
                    />
                  </div>
                  <div>
                    <Label htmlFor="imageUrl">Image URL</Label>
                    <Input
                      id="imageUrl"
                      value={articleData.imageUrl}
                      onChange={(e) => setArticleData({ ...articleData, imageUrl: e.target.value })}
                      placeholder="https://example.com/image.jpg"
                    />
                  </div>
                  <Button onClick={handleGenerateArticle} className="w-full">
                    Generate Article Schema
                  </Button>
                </div>
              )}

              {schemaType === "Product" && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="productName">Product Name *</Label>
                    <Input
                      id="productName"
                      value={productData.name}
                      onChange={(e) => setProductData({ ...productData, name: e.target.value })}
                      placeholder="Enter product name"
                    />
                  </div>
                  <div>
                    <Label htmlFor="productDescription">Description</Label>
                    <Textarea
                      id="productDescription"
                      value={productData.description}
                      onChange={(e) => setProductData({ ...productData, description: e.target.value })}
                      placeholder="Enter product description"
                    />
                  </div>
                  <div>
                    <Label htmlFor="productImage">Image URL</Label>
                    <Input
                      id="productImage"
                      value={productData.imageUrl}
                      onChange={(e) => setProductData({ ...productData, imageUrl: e.target.value })}
                      placeholder="https://example.com/product.jpg"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="price">Price</Label>
                      <Input
                        id="price"
                        value={productData.price}
                        onChange={(e) => setProductData({ ...productData, price: e.target.value })}
                        placeholder="29.99"
                      />
                    </div>
                    <div>
                      <Label htmlFor="currency">Currency</Label>
                      <Input
                        id="currency"
                        value={productData.currency}
                        onChange={(e) => setProductData({ ...productData, currency: e.target.value })}
                        placeholder="USD"
                      />
                    </div>
                  </div>
                  <Button onClick={handleGenerateProduct} className="w-full">
                    Generate Product Schema
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Output Section */}
          <Card>
            <CardHeader>
              <CardTitle>Generated Schema</CardTitle>
              <CardDescription>Copy or download the generated JSON-LD</CardDescription>
            </CardHeader>
            <CardContent>
              {generatedSchema ? (
                <div className="space-y-4">
                  <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-[500px] text-sm">
                    <code>{generatedSchema}</code>
                  </pre>
                  <div className="flex gap-2">
                    <Button onClick={handleCopy} variant="outline" className="flex-1">
                      <Copy className="mr-2 h-4 w-4" />
                      Copy
                    </Button>
                    <Button onClick={handleDownload} variant="outline" className="flex-1">
                      <Download className="mr-2 h-4 w-4" />
                      Download
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-12">
                  Fill in the form and click generate to see the schema
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

