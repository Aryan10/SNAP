"use client";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface NewsItem {
  _id: string; // Assuming the backend returns an _id or unique identifier
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
    media: string[]; // Array of image URLs
    content: string; // Assuming this might contain the image URL if not in media? Or maybe the text content from the source? Using 'media' for images.
  };
  id: string,
}

export default function NewsDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { newsId: encodedTitle } = params;
  // Decode the title from the URL
  const newsId = decodeURIComponent(encodedTitle as string);

  const [newsItem, setNewsItem] = useState<NewsItem | null>(null);
  const [moreNewsItems, setMoreNewsItems] = useState<NewsItem[]>([]); // State for other news
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null); // State for errors

  useEffect(() => {
    const token = localStorage.getItem("SNAPtoken");
    if (!token) {
      router.push("/register");
      return;
    }

    const fetchNews = async () => {
      setLoading(true);
      setError(null); // Clear previous errors

      try {
        // Fetch the specific news item
        const newsItemResponse = await fetch(
          `http://localhost:8000/feeds/${newsId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!newsItemResponse.ok) {
          // Handle cases like 404 Not Found specifically
          if (newsItemResponse.status === 404) {
             setNewsItem(null); // Explicitly set to null for Not Found state
             setMoreNewsItems([]); // No other news if main is not found
          } else {
             throw new Error(
               `Failed to fetch news feed: ${newsItemResponse.statusText}`
             );
          }
        } else {
            const newsItemData: NewsItem = await newsItemResponse.json();
            setNewsItem(newsItemData);

            // Fetch all news feeds for the "More News" section
            const allFeedsResponse = await fetch(`http://localhost:8000/feeds`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!allFeedsResponse.ok) {
                // Log this error but don't block the main content display
                console.error("Failed to fetch all news feeds:", allFeedsResponse.statusText);
                setMoreNewsItems([]); // Set to empty array on error
            } else {
                const allFeedsData: NewsItem[] = (await allFeedsResponse.json()).feeds;
                // Filter out the current news item by its title
                const filteredMoreNews = allFeedsData.filter(
                    (item) => item.id !== newsId
                );
                setMoreNewsItems(filteredMoreNews);
            }
        }


      } catch (err) {
        console.error("Error fetching news:", err);
        if (err instanceof Error) {
             setError(err.message);
        } else {
             setError("An unknown error occurred");
        }
        setNewsItem(null); // Ensure newsItem is null if there's a general error
        setMoreNewsItems([]); // Ensure moreNewsItems is empty on error
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [router, newsId]); // Depend on router and newsId

    // Show loading state
    if (loading) {
        return (
          <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
            <div className="animate-pulse grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="md:col-span-2">
                <div className="h-8 bg-gray-200 rounded-md mb-4"></div>
                <div className="h-6 bg-gray-200 rounded-md mb-2"></div>
                <div className="h-4 bg-gray-200 rounded-md mb-4 max-h-[400px]"></div>
                <div className="h-6 bg-gray-200 rounded-md mb-4"></div>
                <div className="h-4 bg-gray-200 rounded-md"></div>
              </div>
              <div className="md:col-span-1">
                 <div className="h-6 bg-gray-200 rounded-md mb-4"></div>
                 <div className="h-20 bg-gray-200 rounded-md mb-2"></div>
                 <div className="h-20 bg-gray-200 rounded-md mb-2"></div>
                 <div className="h-20 bg-gray-200 rounded-md"></div>
              </div>
            </div>
          </div>
        );
      }

    // Show error state (e.g., network issues other than 404)
    if (error && !newsItem) {
        return (
            <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8 text-red-600">
                <h1 className="text-2xl font-bold mb-4">Error Loading News</h1>
                <p>{error}</p>
                <Link href="/dashboard" className="text-blue-500 hover:underline mt-4 inline-block">
                    Go back to Dashboard
                </Link>
            </div>
        );
    }

    // Show Not Found state (if specific news item fetch resulted in 404)
    if (!newsItem && !loading && !error) {
        return (
            <div className="container max-w-screen-lg mx-auto px-4 sm:px-6 py-8">
                <h1 className="text-2xl font-bold mb-4">News Not Found</h1>
                <p>The requested news article could not be found.</p>
                <Link href="/dashboard" className="text-blue-500 hover:underline mt-4 inline-block">
                    Go back to Dashboard
                </Link>
            </div>
        );
    }

  // Render the news item and more news (only if newsItem is not null)
  if (!newsItem) return null; // Should not happen due to checks above, but good fallback


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

      {/* Layout for main content and sidebar */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-32">
        {/* Main News Content */}
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold mb-4">{newsItem.title}</h1>
          <div className="text-sm text-muted-foreground mb-4">
            Published on{" "}
            {new Date(newsItem.publication_date).toLocaleDateString()} by{" "}
            {newsItem.author || "Unknown"} in {newsItem.category}
          </div>
          {newsItem.source?.media && newsItem.source.media.length > 0 && (
            <div className="aspect-video overflow-hidden bg-muted rounded-md mb-4 max-h-[400px]">
              {/* Use the first image available */}
              <img
                src={newsItem.source.media[0]}
                alt={newsItem.title}
                className="object-cover w-full h-full rounded-md"
              />
            </div>
          )}
          <div className="prose prose-sm sm:prose lg:prose-lg xl:prose-xl dark:prose-invert max-w-none">
            {/* Render content which is often markdown */}
            <ReactMarkdown>{newsItem.content}</ReactMarkdown>
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
        </div>

        {/* More News Sidebar */}
        <div className="md:col-span-1">
            <h2 className="text-xl font-bold mb-4">More News</h2>
            {moreNewsItems.length === 0 ? (
                <p className="text-muted-foreground text-sm">No other news available.</p>
            ) : (
                <ul className="space-y-4"> {/* Add space between list items */}
                    {moreNewsItems.map((item) => (
                        <li key={item._id || item.title}> {/* Use _id if available, fallback to title */}
                            <Link
                                href={`/${encodeURIComponent(item.id)}`} // Link to detail page
                                className="flex items-start hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md p-2 -mx-2 transition-colors"
                            >
                                {item.source?.media && item.source.media.length > 0 && (
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
                                    {/* Optionally add a brief summary or date here */}
                                    {/* <p className="text-xs text-muted-foreground mt-1">{new Date(item.publication_date).toLocaleDateString()}</p> */}
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