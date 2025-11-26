'use client'

import { useState } from 'react'

interface SemanticResult {
    name: string
    similarity: number
    category: string
    features?: {
        tropical_score?: number
        citrus_score?: number
        alcohol_strength?: number
    }
}

interface RAGContext {
    retrieved_docs: Array<{
        name: string
        content: string
        rank: number
    }>
    context_text: string
}

interface AgentAction {
    tool: string
    inputs: Record<string, any>
    outputs: any
    latency_ms: number
    timestamp: string
}

interface DebugData {
    semantic?: {
        query_embedding?: number[]
        top_k_results: SemanticResult[]
        search_method: string
    }
    rag?: RAGContext
    agent?: {
        actions: AgentAction[]
        total_tools_used: number
    }
}

export default function DebugPanel({ data }: { data?: DebugData }) {
    const [activeTab, setActiveTab] = useState<'semantic' | 'rag' | 'agent'>('semantic')

    if (!data) return null

    return (
        <div className="mt-8 border-2 border-blue-100 rounded-xl overflow-hidden bg-white shadow-lg">
            {/* Header */}
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white p-4 flex justify-between items-center">
                <div>
                    <h3 className="text-lg font-bold flex items-center gap-2">
                        ⚡ Live GenAI Engineering Pipeline
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">Real-time execution trace</p>
                </div>
                {/* Mini Badges */}
                <div className="flex gap-2">
                    <span className="text-[10px] bg-blue-500/20 border border-blue-400/30 px-2 py-1 rounded text-blue-200 font-mono">Bedrock</span>
                    <span className="text-[10px] bg-purple-500/20 border border-purple-400/30 px-2 py-1 rounded text-purple-200 font-mono">Vector</span>
                    <span className="text-[10px] bg-green-500/20 border border-green-400/30 px-2 py-1 rounded text-green-200 font-mono">RAG</span>
                </div>
            </div>

            {/* Tabs Navigation */}
            <div className="flex border-b border-gray-100 bg-gray-50/50">
                <button
                    onClick={() => setActiveTab('semantic')}
                    className={`flex-1 py-3 text-sm font-semibold flex items-center justify-center gap-2 transition-colors ${activeTab === 'semantic'
                        ? 'bg-white text-blue-600 border-t-2 border-blue-500 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                        }`}
                >
                    <span>🔍</span> Vector Search
                </button>
                <button
                    onClick={() => setActiveTab('rag')}
                    className={`flex-1 py-3 text-sm font-semibold flex items-center justify-center gap-2 transition-colors ${activeTab === 'rag'
                        ? 'bg-white text-orange-600 border-t-2 border-orange-500 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                        }`}
                >
                    <span>📄</span> RAG Context
                </button>
                <button
                    onClick={() => setActiveTab('agent')}
                    className={`flex-1 py-3 text-sm font-semibold flex items-center justify-center gap-2 transition-colors ${activeTab === 'agent'
                        ? 'bg-white text-purple-600 border-t-2 border-purple-500 shadow-sm'
                        : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                        }`}
                >
                    <span>🤖</span> Agent Actions
                </button>
            </div>

            {/* Tab Content */}
            <div className="p-6 bg-white min-h-[300px]">
                {/* Section 1: Semantic Search */}
                {activeTab === 'semantic' && data.semantic && (
                    <div className="animate-in fade-in duration-300">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="bg-blue-100 p-2 rounded-lg text-xl">🔍</div>
                            <div>
                                <h4 className="font-bold text-gray-900">Semantic Vector Search</h4>
                                <p className="text-xs text-gray-500">Titan Embeddings v2 (1536-dim) • Cosine Similarity</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                                <p className="text-xs font-bold text-gray-500 mb-3 uppercase tracking-wider">Query Embedding Vector</p>
                                <div className="font-mono text-[10px] text-gray-600 break-all leading-relaxed bg-white p-3 rounded border border-gray-100 shadow-inner">
                                    [{data.semantic.query_embedding?.slice(0, 8).map(v => v.toFixed(3)).join(', ')}...]
                                    <span className="text-gray-400 ml-1 block mt-1">(1536 dimensions total)</span>
                                </div>
                            </div>

                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                                <p className="text-xs font-bold text-gray-500 mb-3 uppercase tracking-wider">Top-K Retrieval Results</p>
                                <div className="space-y-2">
                                    {data.semantic.top_k_results.slice(0, 5).map((result, idx) => (
                                        <div key={idx} className="bg-white p-3 rounded border border-gray-100 shadow-sm hover:border-blue-200 transition-colors">
                                            <div className="flex justify-between items-start mb-2">
                                                <div>
                                                    <span className="text-sm font-bold text-gray-800">{result.name}</span>
                                                    <span className="text-xs text-gray-400 ml-2">({result.category})</span>
                                                </div>
                                                <span className="text-xs font-mono bg-green-100 text-green-700 px-2 py-1 rounded-full font-bold">
                                                    {result.similarity.toFixed(3)} similarity
                                                </span>
                                            </div>

                                            {/* The Cute Badges */}
                                            <div className="flex flex-wrap gap-2">
                                                <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded text-[10px] font-medium border border-blue-100">
                                                    🌴 tropical: {result.features?.tropical_score?.toFixed(2) || '0.00'}
                                                </span>
                                                <span className="inline-flex items-center gap-1 bg-yellow-50 text-yellow-700 px-2 py-1 rounded text-[10px] font-medium border border-yellow-100">
                                                    🍋 citrus: {result.features?.citrus_score?.toFixed(2) || '0.00'}
                                                </span>
                                                <span className="inline-flex items-center gap-1 bg-red-50 text-red-700 px-2 py-1 rounded text-[10px] font-medium border border-red-100">
                                                    🍷 strength: {result.features?.alcohol_strength?.toFixed(2) || '0.00'}
                                                </span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Section 2: RAG Context */}
                {activeTab === 'rag' && data.rag && (
                    <div className="animate-in fade-in duration-300">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="bg-orange-100 p-2 rounded-lg text-xl">📄</div>
                            <div>
                                <h4 className="font-bold text-gray-900">RAG Context Assembly</h4>
                                <p className="text-xs text-gray-500">Retrieved Context • Grounded Generation</p>
                            </div>
                        </div>

                        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                            <p className="text-xs font-bold text-gray-500 mb-3 uppercase tracking-wider">LLM Prompt Context Window</p>
                            <pre className="text-xs text-gray-600 font-mono whitespace-pre-wrap bg-white p-4 rounded border border-gray-100 shadow-inner max-h-60 overflow-y-auto">
                                {data.rag.context_text}
                            </pre>
                            <div className="mt-2 text-[10px] text-gray-400 text-right">
                                Context Length: {data.rag.context_text.length} chars
                            </div>
                        </div>
                    </div>
                )}

                {/* Section 3: Agent Actions */}
                {activeTab === 'agent' && data.agent && (
                    <div className="animate-in fade-in duration-300">
                        <div className="flex items-center gap-2 mb-6">
                            <div className="bg-purple-100 p-2 rounded-lg text-xl">🤖</div>
                            <div>
                                <h4 className="font-bold text-gray-900">Agentic Tool Execution</h4>
                                <p className="text-xs text-gray-500">Autonomous Reasoning • Tool Orchestration</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {data.agent.actions.map((action, idx) => (
                                <div key={idx} className="bg-slate-900 text-slate-200 p-5 rounded-xl font-mono text-xs shadow-lg border border-slate-700">
                                    <div className="flex justify-between items-center mb-4 border-b border-slate-700 pb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded text-[10px] uppercase tracking-wide">Tool Call</span>
                                            <span className="text-white font-bold text-sm">{action.tool}</span>
                                        </div>
                                        <span className="text-slate-400 bg-slate-800 px-2 py-1 rounded">{action.latency_ms}ms</span>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div>
                                            <span className="text-slate-500 block mb-2 text-[10px] uppercase tracking-wider">INPUTS</span>
                                            <div className="bg-black/30 p-3 rounded text-green-400 overflow-x-auto border border-white/5">
                                                {JSON.stringify(action.inputs, null, 2)}
                                            </div>
                                        </div>
                                        <div>
                                            <span className="text-slate-500 block mb-2 text-[10px] uppercase tracking-wider">OUTPUTS</span>
                                            <div className="bg-black/30 p-3 rounded text-blue-400 overflow-x-auto border border-white/5 max-h-32">
                                                {JSON.stringify(action.outputs, null, 2)}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
