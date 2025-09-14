import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Repository } from '@/types';

interface RepositoryContextType {
  selectedRepository: Repository | null;
  setSelectedRepository: (repository: Repository | null) => void;
  repositories: Repository[];
  setRepositories: (repositories: Repository[]) => void;
}

const RepositoryContext = createContext<RepositoryContextType | undefined>(undefined);

export function RepositoryProvider({ children }: { children: ReactNode }) {
  const [selectedRepository, setSelectedRepository] = useState<Repository | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);

  return (
    <RepositoryContext.Provider
      value={{
        selectedRepository,
        setSelectedRepository,
        repositories,
        setRepositories,
      }}
    >
      {children}
    </RepositoryContext.Provider>
  );
}

export function useRepository() {
  const context = useContext(RepositoryContext);
  if (context === undefined) {
    throw new Error('useRepository must be used within a RepositoryProvider');
  }
  return context;
}
