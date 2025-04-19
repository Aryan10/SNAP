"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";

interface NewsItem {
  title: string;
  author: string;
  publication_date: string;
  summary: string;
  content: string;
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
  const [loading, setLoading] = useState(true);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("SNAPtoken");
    if (!token) {
      router.push("/register");
      return;
    }

    const fetchNews = async () => {
      try {
        const response = await fetch(`http://localhost:8000/feeds/${newsId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) throw new Error("Failed to fetch news feed");
        const data = await response.json();
        if (!data) setNewsItem(null);
        else setNewsItem(data as NewsItem);
        startTimeRef.current = Date.now(); // Start tracking time
      } catch (error) {
        console.error("Error fetching news:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();

    const handleBeforeUnload = () => {
      sendDuration();
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      sendDuration(); // when component unmounts
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [router, newsId]);
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

  if (loading) {
    return (
      <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded-md mb-4"></div>
          <div className="h-6 bg-gray-200 rounded-md mb-2"></div>
          <div className="h-4 bg-gray-200 rounded-md mb-4 max-h-[400px]"></div>
          <div className="h-6 bg-gray-200 rounded-md mb-4"></div>
          <div className="h-4 bg-gray-200 rounded-md"></div>
        </div>
      </div>
    );
  }

  if (!newsItem) {
    return (
      <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
        <h1 className="text-2xl font-bold mb-4">News Not Found</h1>
        <Link href="/dashboard" className="text-blue-500 hover:underline">
          Go back to Dashboard
        </Link>
      </div>
    );
  }

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
      <h1 className="text-3xl font-bold mb-4">{newsItem.title}</h1>
      <div className="text-sm text-muted-foreground mb-2">
        Published on {new Date(newsItem.publication_date).toLocaleDateString()}{" "}
        by {newsItem.author || "Unknown"} in {newsItem.category}
      </div>
      {newsItem.source.media && newsItem.source.media.length > 0 && (
        <div className="aspect-video overflow-hidden bg-muted rounded-md mb-4 max-h-[400px]">
          <img
            src={newsItem.source.media[0]}
            alt={newsItem.title}
            className="object-cover w-full h-full rounded-md"
          />
        </div>
      )}
      <div className="prose prose-sm sm:prose lg:prose-lg xl:prose-xl dark:prose-invert max-w-none">
        <ReactMarkdown>{newsItem.content}</ReactMarkdown>
      </div>
      {newsItem.source.url && (
        <p className="mt-4 text-sm text-muted-foreground">
          Source:{" "}
          <Link
            href={newsItem.source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-500 hover:underline"
          >
            {newsItem.source.title}
          </Link>
        </p>
      )}
    </div>
  );
}
