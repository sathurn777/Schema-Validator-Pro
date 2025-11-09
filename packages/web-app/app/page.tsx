import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Code2, CheckCircle2, Zap, Shield } from "lucide-react";

export default function Home() {
  return (
    <div className="flex flex-col">
      <section className="container flex flex-col items-center gap-6 pb-8 pt-6 md:py-10">
        <div className="flex max-w-[980px] flex-col items-center gap-4 text-center">
          <h1 className="text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:text-6xl lg:leading-[1.1]">
            Schema.org JSON-LD
            <br className="hidden sm:inline" />
            {" "}Generator & Validator
          </h1>
          <p className="max-w-[750px] text-lg text-muted-foreground sm:text-xl">
            Generate and validate Schema.org structured data for better SEO.
          </p>
        </div>
        <div className="flex gap-4">
          <Link href="/generate">
            <Button size="lg">
              <Code2 className="mr-2 h-4 w-4" />
              Generate Schema
            </Button>
          </Link>
          <Link href="/validate">
            <Button size="lg" variant="outline">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Validate Schema
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
