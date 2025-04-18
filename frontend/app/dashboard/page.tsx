"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Newspaper, Settings, LogOut } from "lucide-react"

export default function DashboardPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("SNAPtoken")
    if (!token) {
      router.push("/register")
      return
    }

    // Simulate loading news data
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("token")
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
          {/* Sample news cards - in a real app, these would be populated from API */}
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <NewsCard key={item} />
          ))}
        </div>
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>© {new Date().getFullYear()} NewsAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}

function NewsCard() {
  // Generate random content for demo purposes
  const categories = ["Technology", "Business", "Science", "Health", "World"]
  const category = categories[Math.floor(Math.random() * categories.length)]

  const titles = [
    "New AI Model Achieves Breakthrough in Natural Language Understanding",
    "Renewable Energy Investments Reach All-Time High",
    "Scientists Discover Potential Treatment for Rare Disease",
    "Global Economy Shows Signs of Recovery",
    "New Study Reveals Benefits of Mediterranean Diet",
  ]
  const title = titles[Math.floor(Math.random() * titles.length)]

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="text-sm font-medium text-primary mb-1">{category}</div>
        <CardTitle className="text-xl">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore
          magna aliqua.
        </p>
      </CardContent>
      <CardFooter className="flex justify-between">
        <div className="text-sm text-muted-foreground">{new Date().toLocaleDateString()}</div>
        <Button variant="ghost" size="sm">
          Read More
        </Button>
      </CardFooter>
    </Card>
  )
}
