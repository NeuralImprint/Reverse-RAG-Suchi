import { useState, useCallback } from 'react';

export function useSuchiStream() {
  const [streamData, setStreamData] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startStream = useCallback(async (prompt: string) => {
    setIsStreaming(true);
    setStreamData("");
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let done = false;
      
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        
        if (value) {
          const chunk = decoder.decode(value, { stream: !done });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
               const dataStr = line.substring(6).trim();
               if (dataStr === '[DONE]') {
                 setIsStreaming(false);
                 return;
               }
               if (dataStr) {
                 try {
                   const data = JSON.parse(dataStr);
                   if (data.error) {
                     setError(data.error);
                     setIsStreaming(false);
                     return;
                   }
                   if (data.text) {
                     setStreamData(prev => prev + data.text);
                   }
                 } catch (e) {
                   console.error("JSON parse error:", e, dataStr);
                 }
               }
            }
          }
        }
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsStreaming(false);
    }
  }, []);

  return { streamData, isStreaming, error, startStream };
}
