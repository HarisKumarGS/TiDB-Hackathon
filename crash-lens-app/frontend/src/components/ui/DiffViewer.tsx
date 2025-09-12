import React from 'react';
import { Diff, Hunk, parseDiff } from 'react-diff-view';
import 'react-diff-view/style/index.css';
import './DiffViewer.css';

interface DiffViewerProps {
  diffText: string;
  className?: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diffText, className = '' }) => {
  if (!diffText) {
    return (
      <div className={`p-4 text-muted-foreground text-center ${className}`}>
        No diff available
      </div>
    );
  }

  try {
    // Parse the diff text
    const files = parseDiff(diffText);
    
    if (!files || files.length === 0) {
      return (
        <div className={`p-4 text-muted-foreground text-center ${className}`}>
          Invalid diff format
        </div>
      );
    }

    return (
      <div className={`diff-viewer ${className}`}>
        {files.map((file, index) => (
          <div key={index} className="mb-4">
            {/* File header */}
            <div className="bg-muted/50 px-4 py-2 border-b font-mono text-sm">
              <span className="text-destructive">--- {file.oldPath}</span>
              <br />
              <span className="text-green-600">+++ {file.newPath}</span>
            </div>
            
            {/* Diff content */}
            <Diff 
              viewType="unified" 
              diffType={file.type}
              hunks={file.hunks}
              className="diff-content"
            >
              {(hunks) => hunks.map((hunk) => (
                <Hunk key={hunk.content} hunk={hunk} />
              ))}
            </Diff>
          </div>
        ))}
      </div>
    );
  } catch (error) {
    console.error('Error parsing diff:', error);
    
    // Fallback to simple pre element if parsing fails
    return (
      <div className={`bg-secondary/20 rounded-lg p-4 font-mono text-sm overflow-x-auto ${className}`}>
        <pre className="whitespace-pre-wrap">{diffText}</pre>
      </div>
    );
  }
};
