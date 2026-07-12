import React, { useMemo } from 'react';

interface Props {
  text: string;
}

export const SuchiStreamRenderer: React.FC<Props> = ({ text }) => {
  const parsedNodes = useMemo(() => {
    // Regex to match <correction source="metadata_name">...</correction>
    const regex = /<correction\s+source="([^"]+)">([\s\S]*?)<\/correction>/g;
    const nodes: React.ReactNode[] = [];
    
    let lastIndex = 0;
    let match;
    
    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        nodes.push(<span key={lastIndex}>{text.substring(lastIndex, match.index)}</span>);
      }
      
      const source = match[1];
      const correctedText = match[2];
      
      nodes.push(
        <span 
          key={match.index} 
          className="group relative inline-block bg-green-900/30 text-green-400 font-medium px-1 rounded mx-0.5 cursor-pointer underline decoration-green-500/50 decoration-dashed underline-offset-4 transition-colors hover:bg-green-800/40"
        >
          {correctedText}
          <span className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-max max-w-xs break-words px-3 py-1.5 bg-slate-800 text-xs text-slate-200 rounded opacity-0 invisible group-hover:visible group-hover:opacity-100 transition-all font-mono border border-slate-700 shadow-xl z-10 pointer-events-none before:absolute before:top-full before:left-1/2 before:-translate-x-1/2 before:border-[6px] before:border-transparent before:border-t-slate-800">
            Source: {source}
          </span>
        </span>
      );
      
      lastIndex = regex.lastIndex;
    }
    
    if (lastIndex < text.length) {
      nodes.push(<span key={lastIndex}>{text.substring(lastIndex)}</span>);
    }
    
    return nodes;
  }, [text]);

  return (
    <div className="text-left text-lg leading-relaxed text-slate-300 font-sans tracking-wide">
      {parsedNodes}
    </div>
  );
};
