import { Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';

export function Header() {
  return (
    <header className="flex items-center justify-between h-16 px-4 sm:px-6 glass border-b border-border/30">
      {/* App Title - Hidden on mobile when sidebar is present */}
      <div className="flex items-center">
        <h2 className="text-lg font-semibold gradient-text hidden sm:block">
          CrashLens Dashboard
        </h2>
      </div>
    </header>
  );
}