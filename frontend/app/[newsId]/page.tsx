"use client";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useState, useRef } from "react";
import Location from "./location";
interface NewsItem {
  _id: string;
  title: string;
  author: string;
  publication_date: string;
  summary: string;
  content: string;
  markdown_content: string;
  category: string;
  tags: string[];
  source: {
    title: string;
    url: string;
    created_utc: number;
    subreddit: string;
    media: string[];
    content: string;
  };
  location: string | null;
  duration: number;
  popularity: number;
  id: string;
}

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { newsId: encodedTitle } = params;
  const newsId = decodeURIComponent(encodedTitle as string);

  const [newsItem, setNewsItem] = useState<NewsItem | null>(null);
  const [moreNewsItems, setMoreNewsItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const startTimeRef = useRef<number | null>(null);

  const sendDuration = async () => {
    if (!startTimeRef.current) return;
    const token = localStorage.getItem("SNAPtoken");
    const durationMs = Date.now() - startTimeRef.current;

    try {
      await fetch(`http://localhost:8000/feeds/${newsId}/track_time`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ durationMs }),
      });
    } catch (err) {
      console.error("Failed to track article duration:", err);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const token = localStorage.getItem("SNAPtoken");

    if (!token) {
      router.push("/register");
      return;
    }

    const fetchNews = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`http://localhost:8000/feeds/${newsId}`, {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });

        if (!res.ok) {
          if (res.status === 404) {
            setNewsItem(null);
            setMoreNewsItems([]);
            return;
          }
          throw new Error("Failed to fetch news feed");
        }

        const newsData: NewsItem = await res.json();
        setNewsItem(newsData);
        startTimeRef.current = Date.now();

        const allFeedsRes = await fetch("http://localhost:8000/feeds", {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });

        if (allFeedsRes.ok) {
          const feeds: { feeds: NewsItem[] } = await allFeedsRes.json();
          setMoreNewsItems(feeds.feeds.filter((item) => item.id !== newsId));
        } else {
          setMoreNewsItems([]);
        }
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") return;
        console.error("Error fetching news:", err);
        setError((err as Error).message || "An unknown error occurred");
        setNewsItem(null);
        setMoreNewsItems([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();

    const handleBeforeUnload = () => sendDuration();
    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      sendDuration();
      controller.abort();
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [router, newsId]);

  // Loading State
  if (loading) {
    return (
      <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
        <div className="animate-pulse grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-4">
            <div className="h-8 bg-gray-200 rounded-md" />
            <div className="h-6 bg-gray-200 rounded-md" />
            <div className="h-4 bg-gray-200 rounded-md max-h-[400px]" />
            <div className="h-6 bg-gray-200 rounded-md" />
            <div className="h-4 bg-gray-200 rounded-md" />
          </div>
          <div className="md:col-span-1 space-y-4">
            <div className="h-6 bg-gray-200 rounded-md" />
            <div className="h-20 bg-gray-200 rounded-md" />
            <div className="h-20 bg-gray-200 rounded-md" />
            <div className="h-20 bg-gray-200 rounded-md" />
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error && !newsItem) {
    return (
      <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8 text-red-600">
        <h1 className="text-2xl font-bold mb-4">Error Loading News</h1>
        <p>{error}</p>
        <Link
          href="/dashboard"
          className="text-blue-500 hover:underline mt-4 inline-block"
        >
          Go back to Dashboard
        </Link>
      </div>
    );
  }

  // Not Found State
  if (!newsItem && !loading && !error) {
    return (
      <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
        <h1 className="text-2xl font-bold mb-4">News Not Found</h1>
        <p>The requested news article could not be found.</p>
        <Link
          href="/dashboard"
          className="text-blue-500 hover:underline mt-4 inline-block"
        >
          Go back to Dashboard
        </Link>
      </div>
    );
  }

  // Final Fallback
  if (!newsItem) return null;

  // Render News Content
  return (
    <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="inline-flex items-center text-blue-500 hover:underline"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-32">
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold mb-4">{newsItem.title}</h1>
          <div className="text-sm text-muted-foreground mb-4">
            Published on{" "}
            {new Date(newsItem.publication_date).toLocaleDateString()} by{" "}
            {newsItem.author || "Unknown"} in {newsItem.category}
          </div>
          {newsItem.source?.media?.[0] && (
            <div className="bg-muted rounded-md mb-4">
              <img
                src={newsItem.source.media[0]}
                alt={newsItem.title}
                className="object-cover w-full h-full rounded-md"
              />
            </div>
          )}
          <div className="prose dark:prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {newsItem.markdown_content.replace(/\\n/g, "\n")}
            </ReactMarkdown>
          </div>
          {newsItem.source?.url && (
            <p className="mt-4 text-sm text-muted-foreground">
              Source:{" "}
              <Link
                href={newsItem.source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                {newsItem.source.title || "Link"}
              </Link>
            </p>
          )}
          {newsItem?.location && <Location location={newsItem.location} />}
        </div>

        {/* More News Section */}
        <div className="md:col-span-1">
          <h2 className="text-xl font-bold mb-4">More News</h2>
          {moreNewsItems.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No other news available.
            </p>
          ) : (
            <ul className="space-y-4">
              {moreNewsItems.map((item) => (
                <li key={item._id || item.id}>
                  <Link
                    href={`/${encodeURIComponent(item.id)}`}
                    className="flex items-start hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md p-2 -mx-2 transition-colors"
                  >
                    {item.source?.media?.[0] && (
                      <div className="w-16 h-16 flex-shrink-0 mr-3 overflow-hidden rounded-md bg-muted">
                        <img
                          src={item.source.media[0]}
                          alt={item.title}
                          className="object-cover w-full h-full"
                        />
                      </div>
                    )}
                    <div className="flex-grow">
                      <h3 className="text-sm font-semibold leading-tight">
                        {item.title}
                      </h3>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
