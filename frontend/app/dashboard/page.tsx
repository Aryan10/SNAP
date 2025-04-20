"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Newspaper,
  Settings,
  LogOut,
  MessageCircle,
  X,
  Send,
} from "lucide-react";

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
  id: string;
}

interface ChatMessage {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export default function DashboardPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const bottomSentinel = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isFetchingRef = useRef(false);
  const ITEMS_PER_PAGE = 9;

  // Chat state
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      console.log(scrollTop, scrollHeight, clientHeight);
    }
  }, [containerRef]);

  const fetchNews = useCallback(async (pageNum: number) => {
    const token = localStorage.getItem("SNAPtoken");
    if (!token) return;

    try {
      isFetchingRef.current = true;
      setLoadingMore(pageNum > 1);

      const res = await fetch(
        `http://localhost:8000/feeds/${pageNum}/${ITEMS_PER_PAGE}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!res.ok) throw new Error("Failed to fetch news");

      const { feeds, has_more } = await res.json();
      console.log("HAS MORE", has_more);
      const newArticles = feeds as NewsItem[];

      // update hasMore from API or fallback
      setHasMore(has_more ?? newArticles.length === ITEMS_PER_PAGE);

      setNews((prev) =>
        pageNum === 1 ? newArticles : [...prev, ...newArticles]
      );
    } catch (err) {
      console.error("Error fetching news:", err);
    } finally {
      isFetchingRef.current = false;
      setIsLoading(false);
      setLoadingMore(false);
    }
  }, []);

  const handleScroll = () => {
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      console.log(scrollHeight, scrollHeight, scrollTop, clientHeight);
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        setPage((p) => p + 1);
      }
    }
  };

  // 1) On mount, check auth and load first page
  useEffect(() => {
    if (!localStorage.getItem("SNAPtoken")) {
      router.push("/register");
      return;
    }
    fetchNews(1);
  }, [router, fetchNews]);

  // Auto-scroll chat to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isChatOpen) {
      inputRef.current?.focus();
    }
  }, [isChatOpen]);

  const handleLogout = () => {
    localStorage.removeItem("SNAPtoken");
    router.push("/");
  };

  useEffect(() => {
    if (hasMore) {
      console.log(page);
      fetchNews(page);
    }
  }, [page]);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim()) return;

    const token = localStorage.getItem("SNAPtoken");
    if (!token) return;

    // Add user message to chat
    const userMessage: ChatMessage = {
      text: inputMessage,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();
      console.log(data);
      // Add bot response to chat
      const botMessage: ChatMessage = {
        text: data.response || "Sorry, I couldn't process your request.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      // Add error message
      const errorMessage: ChatMessage = {
        text: "Sorry, there was an error processing your request. Please try again.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        {/* ... your existing loading UI ... */}
        <main className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-semibold mb-2">
              Loading your personalized news feed...
            </h2>
            <p className="text-muted-foreground">
              Please wait while we gather the latest news for you.
            </p>
          </div>
        </main>
      </div>
    );
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

        <div
          ref={containerRef}
          onScroll={handleScroll}
          className="overflow-y-auto no-scrollbar grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          style={{ height: "70vh" }}
        >
          {news.map((item, idx) => (
            <NewsCard key={`${item.id}-${idx}`} newsItem={item} />
          ))}
        </div>

        {/* bottom sentinel */}
        <div ref={bottomSentinel} className="h-1" />

        {/* loading indicator or end message */}
        <div className="mt-4 text-center">
          {loadingMore && (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          )}
          {!hasMore && (
            <p className="text-muted-foreground">
              You've reached the end of your feed
            </p>
          )}
        </div>
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© {new Date().getFullYear()} NewsAI. All rights reserved.</p>
        </div>
      </footer>

      {/* Floating Chat Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isChatOpen ? (
          <Button
            onClick={toggleChat}
            className="h-14 w-14 rounded-full shadow-lg flex items-center justify-center"
          >
            <MessageCircle className="h-6 w-6" />
          </Button>
        ) : (
          <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-80 sm:w-96 flex flex-col"
            style={{ height: "500px" }}
          >
            {/* Chat Header */}
            <div className="p-4 border-b flex justify-between items-center">
              <h3 className="font-semibold">NewsAI Assistant</h3>
              <Button variant="ghost" size="icon" onClick={toggleChat}>
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 p-4 overflow-y-auto">
              {messages.length === 0 ? (
                <div className="h-full flex items-center justify-center text-center text-muted-foreground">
                  <div>
                    <MessageCircle className="h-10 w-10 mx-auto mb-2 opacity-50" />
                    <p>Ask me anything about the news!</p>
                  </div>
                </div>
              ) : (
                <>
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`mb-4 flex ${
                        msg.isUser ? "justify-end" : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-3/4 p-3 rounded-lg ${
                          msg.isUser
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        <ReactMarkdown>
                          {msg.text.replaceAll("\n", "\n\n")}
                        </ReactMarkdown>
                        <div className="text-xs opacity-70 mt-1">
                          {msg.timestamp.toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </div>
                      </div>
                    </div>
                  ))}
                  {isTyping && (
                    <div className="mb-4 flex justify-start">
                      <div className="max-w-3/4 p-3 rounded-lg bg-muted flex space-x-1">
                        <div
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: "200ms" }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: "400ms" }}
                        ></div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={sendMessage} className="p-4 border-t flex gap-2">
              <input
                type="text"
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 bg-muted rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={isTyping}
              />
              <Button
                type="submit"
                size="icon"
                disabled={isTyping || !inputMessage.trim()}
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

interface NewsCardProps {
  newsItem: NewsItem;
}

function NewsCard({ newsItem }: NewsCardProps) {
  return (
    <Link href={`/${encodeURIComponent(newsItem.id)}`}>
      <Card className="cursor-pointer hover:shadow-md transition-shadow duration-200 px-5 min-h-[200px] pt-5">
        <div className="flex items-start gap-4">
          <div className="flex-1">
            <div className="text-sm font-medium text-primary mb-1">
              {newsItem.category}
            </div>
            <CardTitle className="text-xl line-clamp-2">
              {newsItem.title}
            </CardTitle>
          </div>
          {newsItem.source.media?.[0] && (
            <img
              src={newsItem.source.media[0]}
              alt={newsItem.title}
              className="w-28 h-28 object-cover rounded-md"
            />
          )}
        </div>
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
  );
}
