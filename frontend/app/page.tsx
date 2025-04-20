import type React from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Newspaper,
  Zap,
  Filter,
  RefreshCw,
  Shield,
  Lightbulb,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Newspaper className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">DistillNews</h1>
          </div>
          <Link href="/register">
            <Button>
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <section className="py-20 px-4">
          <div className="container mx-auto max-w-5xl text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              News That Matters,{" "}
              <span className="text-primary">Refined by AI</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-10 max-w-3xl mx-auto">
              We gather news from every source, filter out the noise, and
              deliver only the most relevant, high-quality content tailored to
              your interests.
            </p>
            <Link href="/register">
              <Button size="lg" className="px-8">
                Start Reading Smarter
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </section>

        <section className="bg-muted py-20 px-4">
          <div className="container mx-auto max-w-6xl">
            <h2 className="text-3xl font-bold text-center mb-12">
              Why DistillNews is Better
            </h2>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<RefreshCw className="h-10 w-10 text-primary" />}
                  title="Daily Updates"
                  description="Our AI scans thousands of sources and updates your feed every 24 hours with fresh, relevant content."
                />
              </div>
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<Filter className="h-10 w-10 text-primary" />}
                  title="Personalized Feed"
                  description="Get news tailored to your preferences and interests, so you only see what matters to you."
                />
              </div>
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<Shield className="h-10 w-10 text-primary" />}
                  title="Unbiased Reporting"
                  description="Our AI removes political bias and sensationalism, delivering balanced and factual news."
                />
              </div>
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<Zap className="h-10 w-10 text-primary" />}
                  title="Smart Summaries"
                  description="Get concise AI-generated summaries of complex news stories to save both time and energy."
                />
              </div>
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<Newspaper className="h-10 w-10 text-primary" />}
                  title="Diverse Sources"
                  description="We aggregate from thousands of sources to ensure you get a complete picture of world events."
                />
              </div>
              <div className="cursor-pointer">
                <FeatureCard
                  icon={<Lightbulb className="h-10 w-10 text-primary" />}
                  title="Contextual Insights"
                  description="Our AI explains background, impact, and context to keep you truly informed."
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-20 px-4">
          <div className="container mx-auto max-w-4xl text-center">
            <h2 className="text-3xl font-bold mb-6">
              Ready to transform your news experience?
            </h2>
            <p className="text-xl text-muted-foreground mb-10">
              Join thousands of readers who've switched to a smarter way to stay
              informed.
            </p>
            <Link href="/register">
              <Button size="lg" className="px-8">
                Get Started Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </section>
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© {new Date().getFullYear()} DistillNews. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-background p-6 rounded-lg shadow-sm border">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}
