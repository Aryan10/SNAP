"use client";

import { useEffect, useState, useRef, useCallback } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Newspaper, Settings, LogOut } from "lucide-react"

interface NewsItem {
  title: string
  author: string
  publication_date: string
  summary: string
  content: string
  category: string
  tags: string[]
  source: {
    title: string
    url: string
    created_utc: number
    subreddit: string
    media: string[]
    content: string
  },
  id: string,
}

export default function DashboardPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [news, setNews] = useState<NewsItem[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const loaderRef = useRef<HTMLDivElement>(null)
  const ITEMS_PER_PAGE = 9

  const fetchNews = useCallback(async (pageNum: number) => {
    const token = localStorage.getItem("SNAPtoken")
    if (!token) return

    try {
      setLoadingMore(pageNum > 1)
      const response = await fetch(`http://localhost:8000/feeds?page=${pageNum}&limit=${ITEMS_PER_PAGE}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
      
      if (!response.ok) {
        throw new Error("Failed to fetch news feed")
      }
      
      const data = await response.json()
      const newArticles = data.feeds as NewsItem[]
      
      // Check if we have more articles to load
      if (newArticles.length < ITEMS_PER_PAGE) {
        setHasMore(false)
      }

      setNews(prevNews => pageNum === 1 ? newArticles : [...prevNews, ...newArticles])
    } catch (error) {
      console.error("Error fetching news:", error)
    } finally {
      setIsLoading(false)
      setLoadingMore(false)
    }
  }, [])

  useEffect(() => {
    const token = localStorage.getItem("SNAPtoken")
    if (!token) {
      router.push("/register")
      return
    }

    fetchNews(1)
  }, [router, fetchNews])

  // Intersection Observer for infinite scrolling
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          setPage(prevPage => prevPage + 1)
        }
      },
      { threshold: 1.0 }
    )

    if (loaderRef.current) {
      observer.observe(loaderRef.current)
    }

    return () => {
      if (loaderRef.current) {
        observer.unobserve(loaderRef.current)
      }
    }
  }, [hasMore, loadingMore])

  // Fetch next page when page changes
  useEffect(() => {
    if (page > 1) {
      fetchNews(page)
    }
  }, [page, fetchNews])

  const handleLogout = () => {
    localStorage.removeItem("SNAPtoken")
    router.push("/")
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <Link href="/" className="flex items-center gap-2">
              <Newspaper className="h-6 w-6 text-primary" />
              <h1 className="text-2xl font-bold">NewsAI</h1>
            </Link>
          </div>
        </header>
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-2">Loading your personalized news feed...</h2>
            <p className="text-muted-foreground">Please wait while we gather the latest news for you.</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2">
            <Newspaper className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">NewsAI</h1>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/preferences">
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Preferences
              </Button>
            </Link>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Your News Feed</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {news.map((item, index) => (
            <NewsCard key={`${item.id}-${index}`} newsItem={item} />
          ))}
        </div>

        {hasMore && (
          <div 
            ref={loaderRef} 
            className="mt-8 text-center py-6"
          >
            {loadingMore ? (
              <div className="flex justify-center items-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : (
              <p className="text-muted-foreground">Scroll for more articles</p>
            )}
          </div>
        )}

        {!hasMore && news.length > 0 && (
          <div className="mt-8 text-center py-6">
            <p className="text-muted-foreground">You've reached the end of your feed</p>
          </div>
        )}
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© {new Date().getFullYear()} NewsAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

interface NewsCardProps {
  newsItem: NewsItem
}

function NewsCard({ newsItem }: NewsCardProps) {
  return (
    <Link href={`/${encodeURIComponent(newsItem.id)}`}>
      <Card className="cursor-pointer hover:shadow-md transition-shadow duration-200">
        <CardHeader className="pb-2">
          <div className="text-sm font-medium text-primary mb-1">{newsItem.category}</div>
          <CardTitle className="text-xl line-clamp-2">{newsItem.title}</CardTitle>
        </CardHeader>
        <CardContent className="aspect-video overflow-hidden bg-muted rounded-md">
          {newsItem.source.media && newsItem.source.media.length > 0 ? (
            <img
              src={newsItem.source.media[0]}
              alt={newsItem.title}
              className="object-cover w-full h-full"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              No Image Available
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between pt-2">
          <div className="text-sm text-muted-foreground">
            {new Date(newsItem.publication_date).toLocaleDateString()}
          </div>
          <Button variant="ghost" size="sm">
            Read More
          </Button>
        </CardFooter>
      </Card>
    </Link>
  )
}