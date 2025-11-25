'use client'

import { useState } from 'react'

export default function Home() {
    const [searchQuery, setSearchQuery] = useState('')
    const [results, setResults] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    const handleSearch = async () => {
        if (!searchQuery.trim()) return

        setLoading(true)
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL
            const response = await fetch(`${apiUrl}/v1/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: searchQuery, k: 5 })
            })

            const data = await response.json()
            setResults(data.results || [])
        } catch (error) {
            console.error('Search error:', error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <main className="min-h-screen">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-6xl font-bold mb-4">🍹 Mocktailverse</h1>
                    <p className="text-2xl mb-2">GenAI Data Engineering Platform</p>
                    <p className="text-lg opacity-90">
                        AWS Bedrock | Semantic Search | RAG | Vector Embeddings
                    </p>
                </div>
            </div>

            {/* Search Section */}
            <div className="container mx-auto px-4 py-12">
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white rounded-lg shadow-lg p-8">
                        <h2 className="text-2xl font-bold mb-4">Semantic Search</h2>
                        <p className="text-gray-600 mb-6">
                            Search for cocktails using natural language. Try: "refreshing summer drinks" or "tropical mocktails"
                        </p>

                        <div className="flex gap-2 mb-6">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder="Search for cocktails..."
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                            <button
                                onClick={handleSearch}
                                disabled={loading}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Searching...' : 'Search'}
                            </button>
                        </div>

                        {/* Results */}
                        {results.length > 0 && (
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold">Results ({results.length})</h3>
                                {results.map((result, idx) => (
                                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                                        <div className="flex justify-between items-start mb-2">
                                            <h4 className="text-lg font-semibold">{result.name}</h4>
                                            <span className="text-sm text-gray-500">
                                                {(result.relevance_score * 100).toFixed(0)}% match
                                            </span>
                                        </div>
                                        <p className="text-gray-600 mb-2">{result.description}</p>
                                        <div className="flex gap-2 flex-wrap">
                                            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                                                {result.category}
                                            </span>
                                            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                                {result.alcoholic}
                                            </span>
                                            {result.difficulty && (
                                                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                                                    {result.difficulty}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Architecture Section */}
            <div className="bg-gray-100 py-12">
                <div className="container mx-auto px-4">
                    <div className="max-w-4xl mx-auto">
                        <h2 className="text-3xl font-bold mb-6 text-center">Architecture</h2>
                        <div className="bg-white rounded-lg shadow-lg p-8">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="text-center">
                                    <div className="text-4xl mb-2">🔄</div>
                                    <h3 className="font-semibold mb-2">Ingestion</h3>
                                    <p className="text-sm text-gray-600">
                                        Lambda + Bedrock Claude for metadata extraction
                                    </p>
                                </div>
                                <div className="text-center">
                                    <div className="text-4xl mb-2">🧠</div>
                                    <h3 className="font-semibold mb-2">Embeddings</h3>
                                    <p className="text-sm text-gray-600">
                                        Bedrock Titan generates 1536-dim vectors
                                    </p>
                                </div>
                                <div className="text-center">
                                    <div className="text-4xl mb-2">🔍</div>
                                    <h3 className="font-semibold mb-2">Search</h3>
                                    <p className="text-sm text-gray-600">
                                        Semantic KNN search with DynamoDB
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <footer className="bg-gray-800 text-white py-8">
                <div className="container mx-auto px-4 text-center">
                    <p className="mb-2">Built with AWS Bedrock, Next.js, and ❤️</p>
                    <p className="text-sm text-gray-400">
                        <a href="https://github.com/anix-lynch/mocktailverse" className="hover:text-white">
                            ⭐ Star on GitHub
                        </a>
                        {' | '}
                        <a href="https://gozeroshot.dev" className="hover:text-white">
                            Portfolio
                        </a>
                    </p>
                </div>
            </footer>
        </main>
    )
}
