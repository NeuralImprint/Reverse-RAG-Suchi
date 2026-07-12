import { useState, useRef } from 'react';
import { useSuchiStream } from './hooks/useSuchiStream';
import { SuchiStreamRenderer } from './components/SuchiStreamRenderer';

function App() {
  const [prompt, setPrompt] = useState("");
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { streamData, isStreaming, error, startStream } = useSuchiStream();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploadStatus("Uploading & processing...");
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) throw new Error("Upload failed");
      const data = await response.json();
      setUploadStatus(`Success: ${data.chunks_processed} chunks added to Qdrant.`);
    } catch (err: any) {
      setUploadStatus(`Error: ${err.message}`);
    }
  };

  const handleChat = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    startStream(prompt);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-8 pt-12 xl:px-32 selection:bg-indigo-500/30">
      <header className="mb-12 flex flex-col sm:flex-row items-center justify-between border-b border-white/5 pb-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 inline-block drop-shadow-sm">
            Project Suchi
          </h1>
          <p className="text-slate-400 mt-2 font-medium">Self-Healing Reverse-RAG Firewall</p>
        </div>
        <div className="mt-6 sm:mt-0">
          <input 
            type="file" 
            className="hidden" 
            ref={fileInputRef} 
            onChange={handleUpload}
            accept=".txt,.pdf"
          />
          <button 
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="px-5 py-2.5 bg-slate-900 border border-slate-700 hover:border-indigo-500/50 hover:bg-slate-800 transition-all rounded-lg text-sm font-semibold shadow-sm focus:ring-2 focus:ring-indigo-500/20"
          >
            Upload Ground Truth
          </button>
          {uploadStatus && (
            <div className="mt-3 text-xs text-indigo-300 font-mono text-right">{uploadStatus}</div>
          )}
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-[calc(100vh-200px)] min-h-[600px]">
        {/* Interaction Panel */}
        <div className="col-span-1 lg:col-span-4 bg-slate-900/50 border border-white/5 backdrop-blur-sm rounded-2xl p-6 flex flex-col h-full shadow-2xl">
          <h2 className="text-xl font-bold mb-4 text-slate-200 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
            Interface
          </h2>
          <form onSubmit={handleChat} className="flex-1 flex flex-col justify-end">
            <div className="bg-slate-950/50 rounded-xl p-1 shadow-inner border border-white/[0.02]">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Trigger the stream..."
                className="w-full bg-transparent text-slate-200 p-4 min-h-[120px] resize-none focus:outline-none placeholder:text-slate-600 font-medium"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleChat(e);
                  }
                }}
              />
              <div className="flex justify-end p-2 border-t border-white/5">
                 <button 
                  type="submit" 
                  disabled={isStreaming || !prompt.trim()}
                  className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold rounded-lg transition-all shadow-lg hover:shadow-indigo-500/20 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
                >
                  Generate Stream
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Streaming Panel */}
        <div className="col-span-1 lg:col-span-8 bg-slate-900/30 border border-white/5 backdrop-blur-md rounded-2xl p-8 relative overflow-hidden shadow-2xl flex flex-col h-full">
          <div className="absolute top-0 right-0 p-4 flex gap-3">
             {isStreaming && (
                <div className="flex items-center gap-2 text-xs font-bold text-amber-500 uppercase tracking-widest bg-amber-500/10 px-3 py-1.5 rounded-full border border-amber-500/20">
                  <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-ping"></div>
                  Intercepting
                </div>
             )}
          </div>
          
          <h2 className="text-sm font-semibold tracking-widest text-slate-500 uppercase mb-6 flex-shrink-0">
            Secure Output
          </h2>
          
          <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar">
            {error ? (
              <div className="text-red-400 bg-red-900/20 p-4 rounded-lg font-mono text-sm border border-red-500/20">{error}</div>
            ) : streamData ? (
              <SuchiStreamRenderer text={streamData} />
            ) : (
              <div className="h-full flex items-center justify-center text-slate-700 italic">
                Awaiting input stream...
              </div>
            )}
            
            {isStreaming && (
               <span className="inline-block w-2 h-5 bg-indigo-500 ml-1 animate-pulse translate-y-1 rounded-[1px]"></span>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
