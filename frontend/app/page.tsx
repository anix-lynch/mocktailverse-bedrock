'use client'

import { useState } from 'react'
import DebugPanel from './components/DebugPanel'

interface Message {
    role: 'user' | 'assistant'
    content: string
    debugData?: any
}

export default function Home() {
    const [message, setMessage] = useState('')
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)
    const [currentDebugData, setCurrentDebugData] = useState<any>(null)
    const sessionId = 'web-session-' + Date.now()

    const handleSend = async () => {
        if (!message.trim()) return

        const userMessage = message
        setMessage('')
        setMessages(prev => [...prev, { role: 'user', content: userMessage }])
        setLoading(true)

        try {
            console.log('Sending request to API...');
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://3m4c6fyw35.execute-api.us-west-2.amazonaws.com/prod'
            const response = await fetch(`${apiUrl}/agent/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: sessionId,
                    debug: true  // Request debug data
                })
            })

            console.log('Response status:', response.status);
            const data = await response.json()
            console.log('API Data:', data);

            // Store debug data
            const debugData = data.debug || null
            console.log('Debug Data:', debugData);
            setCurrentDebugData(debugData)

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.response || data.error || 'Sorry, I could not process that request.',
                debugData
            }])
        } catch (error) {
            console.error('Chat error:', error)
            setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Could not connect to the API. Please check the console.' }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <main className="min-h-screen">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-slate-900 via-purple-900 to-slate-900 text-white py-24">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                        Mocktailverse
                    </h1>
                    <p className="text-2xl mb-8 font-light tracking-wide text-gray-300">
                        Enterprise GenAI Data Engineering Platform
                    </p>

                    {/* ATS Keyword Badges */}
                    <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
                        <span className="px-4 py-2 bg-blue-500/20 border border-blue-500/40 rounded-full text-blue-200 font-mono text-sm">
                            ☁️ AWS Bedrock Serverless
                        </span>
                        <span className="px-4 py-2 bg-purple-500/20 border border-purple-500/40 rounded-full text-purple-200 font-mono text-sm">
                            🧬 Titan Embeddings v2 (1536-dim)
                        </span>
                        <span className="px-4 py-2 bg-green-500/20 border border-green-500/40 rounded-full text-green-200 font-mono text-sm">
                            🔍 Semantic Vector Search
                        </span>
                        <span className="px-4 py-2 bg-orange-500/20 border border-orange-500/40 rounded-full text-orange-200 font-mono text-sm">
                            📄 RAG Pipeline
                        </span>
                        <span className="px-4 py-2 bg-pink-500/20 border border-pink-500/40 rounded-full text-pink-200 font-mono text-sm">
                            🤖 Agentic Tool Orchestration
                        </span>
                        <span className="px-4 py-2 bg-cyan-500/20 border border-cyan-500/40 rounded-full text-cyan-200 font-mono text-sm">
                            ⚡ Next.js 14 + TypeScript
                        </span>
                    </div>
                </div>
            </div>

            {/* Chat Section */}
            <div className="container mx-auto px-4 py-12">
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white rounded-lg shadow-lg p-8">
                        <h2 className="text-2xl font-bold mb-4">🍹 AI Bartender Assistant</h2>
                        <p className="text-gray-600 mb-6">
                            Ask me about cocktails! Try: "What is a mojito?" or "Find me tropical drinks"
                        </p>

                        {/* Chat Messages */}
                        <div className="mb-6 h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
                            {messages.length === 0 ? (
                                <div className="text-center text-gray-500 py-8">
                                    Start a conversation! Ask me about cocktails.
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {messages.map((msg, idx) => (
                                        <div
                                            key={idx}
                                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            <div
                                                className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user'
                                                    ? 'bg-blue-600 text-white'
                                                    : 'bg-white border border-gray-200'
                                                    }`}
                                            >
                                                <p className="whitespace-pre-wrap">{msg.content}</p>
                                            </div>
                                        </div>
                                    ))}
                                    {loading && (
                                        <div className="flex justify-start">
                                            <div className="bg-white border border-gray-200 rounded-lg p-3">
                                                <p className="text-gray-500">Thinking...</p>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && !loading && handleSend()}
                                placeholder="Ask about cocktails..."
                                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                disabled={loading}
                            />
                            <button
                                onClick={handleSend}
                                disabled={loading || !message.trim()}
                                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Sending...' : 'Send'}
                            </button>
                        </div>

                        {/* Debug Panel */}
                        {currentDebugData && (
                            <DebugPanel data={currentDebugData} />
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
