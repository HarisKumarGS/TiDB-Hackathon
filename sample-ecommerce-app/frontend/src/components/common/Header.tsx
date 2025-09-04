import { Link } from 'react-router-dom';
import { Search, ShoppingCart, User, Menu, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useCart } from '@/contexts/CartContext';
import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';

export const Header = () => {
  const { totalItems, openCart } = useCart();
  const { user, isAuthenticated, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 glass border-b border-border/50 backdrop-blur-md">
      <div className="container mx-auto px-4">
        {/* Top Bar */}
        <div className="flex items-center justify-between py-4">
          {/* Logo */}
          <Link 
            to="/" 
            className="flex items-center space-x-2 text-2xl font-bold text-primary hover:text-primary-light transition-smooth"
          >
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">E</span>
            </div>
            <span>EliteStore</span>
          </Link>

          {/* Search Bar - Desktop */}
          <div className="hidden md:flex flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                type="text"
                placeholder="Search products..."
                className="pl-10 pr-4 focus-ring bg-background/50 border-border/50"
              />
            </div>
          </div>

          {/* Navigation Icons */}
          <div className="flex items-center space-x-4">
            {/* Wishlist */}
            <Button variant="ghost" size="icon" className="relative">
              <Heart className="h-5 w-5" />
            </Button>

            {/* Shopping Cart */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="relative"
              onClick={openCart}
            >
              <ShoppingCart className="h-5 w-5" />
              {totalItems > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs"
                >
                  {totalItems}
                </Badge>
              )}
            </Button>

            {/* User Menu */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-2">
                <Button variant="ghost" size="icon">
                  <User className="h-5 w-5" />
                </Button>
                <Button variant="ghost" onClick={logout} className="hidden md:inline-flex">
                  Logout
                </Button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Button variant="ghost" asChild className="hidden md:inline-flex">
                  <Link to="/login">Sign In</Link>
                </Button>
                <Button variant="default" asChild className="hidden md:inline-flex">
                  <Link to="/register">Sign Up</Link>
                </Button>
              </div>
            )}

            {/* Mobile Menu Button */}
            <Button 
              variant="ghost" 
              size="icon" 
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Navigation Links - Desktop */}
        <nav className="hidden md:flex items-center space-x-8 pb-4 border-t border-border/30 pt-4">
          <Link 
            to="/products" 
            className="text-foreground hover:text-primary transition-smooth font-medium"
          >
            All Products
          </Link>
          <Link 
            to="/categories/electronics" 
            className="text-foreground hover:text-primary transition-smooth font-medium"
          >
            Electronics
          </Link>
          <Link 
            to="/categories/fashion" 
            className="text-foreground hover:text-primary transition-smooth font-medium"
          >
            Fashion
          </Link>
          <Link 
            to="/categories/home" 
            className="text-foreground hover:text-primary transition-smooth font-medium"
          >
            Home & Living
          </Link>
          <Link 
            to="/deals" 
            className="text-secondary font-semibold hover:text-secondary-light transition-smooth"
          >
            Special Deals
          </Link>
        </nav>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-border/30 space-y-4 animate-fade-in">
            {/* Mobile Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
              <Input
                type="text"
                placeholder="Search products..."
                className="pl-10 pr-4 focus-ring"
              />
            </div>

            {/* Mobile Navigation Links */}
            <nav className="flex flex-col space-y-3">
              <Link 
                to="/products" 
                className="text-foreground hover:text-primary transition-smooth font-medium py-2"
              >
                All Products
              </Link>
              <Link 
                to="/categories/electronics" 
                className="text-foreground hover:text-primary transition-smooth font-medium py-2"
              >
                Electronics
              </Link>
              <Link 
                to="/categories/fashion" 
                className="text-foreground hover:text-primary transition-smooth font-medium py-2"
              >
                Fashion
              </Link>
              <Link 
                to="/categories/home" 
                className="text-foreground hover:text-primary transition-smooth font-medium py-2"
              >
                Home & Living
              </Link>
              <Link 
                to="/deals" 
                className="text-secondary font-semibold hover:text-secondary-light transition-smooth py-2"
              >
                Special Deals
              </Link>
            </nav>

            {/* Mobile Auth Buttons */}
            {!isAuthenticated && (
              <div className="flex space-x-3 pt-4 border-t border-border/30">
                <Button variant="outline" asChild className="flex-1">
                  <Link to="/login">Sign In</Link>
                </Button>
                <Button variant="default" asChild className="flex-1">
                  <Link to="/register">Sign Up</Link>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};