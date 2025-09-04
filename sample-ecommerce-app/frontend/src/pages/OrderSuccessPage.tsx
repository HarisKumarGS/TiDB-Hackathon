import { Link } from 'react-router-dom';
import { CheckCircle, Package, Mail, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const OrderSuccessPage = () => {
  const orderNumber = '#ORD-' + Math.random().toString(36).substr(2, 9).toUpperCase();

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto text-center">
          {/* Success Icon */}
          <div className="inline-flex items-center justify-center w-24 h-24 bg-accent rounded-full mb-8 animate-scale-in">
            <CheckCircle className="h-12 w-12 text-accent-foreground" />
          </div>

          {/* Success Message */}
          <h1 className="text-4xl font-bold text-foreground mb-4 animate-fade-in">
            Order Confirmed!
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 animate-fade-in">
            Thank you for your purchase. Your order has been successfully placed.
          </p>

          {/* Order Details */}
          <div className="bg-card rounded-xl border border-border/50 shadow-sm p-8 mb-8 animate-slide-up">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
              <div>
                <h3 className="font-semibold text-card-foreground mb-2 flex items-center gap-2">
                  <Package className="h-4 w-4 text-primary" />
                  Order Number
                </h3>
                <p className="text-muted-foreground font-mono">{orderNumber}</p>
              </div>
              
              <div>
                <h3 className="font-semibold text-card-foreground mb-2 flex items-center gap-2">
                  <Mail className="h-4 w-4 text-primary" />
                  Confirmation Email
                </h3>
                <p className="text-muted-foreground">
                  Sent to your registered email address
                </p>
              </div>
            </div>
          </div>

          {/* What's Next */}
          <div className="bg-muted/50 rounded-xl p-8 mb-8 text-left animate-slide-up">
            <h3 className="font-semibold text-foreground mb-4">What happens next?</h3>
            <div className="space-y-3 text-muted-foreground">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm flex items-center justify-center mt-0.5 font-semibold">
                  1
                </div>
                <div>
                  <p className="font-medium">Order Processing</p>
                  <p className="text-sm">We'll prepare your items for shipment</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm flex items-center justify-center mt-0.5 font-semibold">
                  2
                </div>
                <div>
                  <p className="font-medium">Shipping Notification</p>
                  <p className="text-sm">You'll receive tracking information via email</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm flex items-center justify-center mt-0.5 font-semibold">
                  3
                </div>
                <div>
                  <p className="font-medium">Delivery</p>
                  <p className="text-sm">Your order will arrive within 3-7 business days</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up">
            <Button variant="cart" size="lg" asChild>
              <Link to="/orders">
                View Order Status
              </Link>
            </Button>
            
            <Button variant="outline" size="lg" asChild>
              <Link to="/products">
                Continue Shopping
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>

          {/* Support */}
          <div className="mt-12 p-6 bg-gradient-subtle rounded-xl animate-fade-in">
            <p className="text-muted-foreground mb-4">
              Need help with your order?
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button variant="ghost" asChild>
                <Link to="/contact">Contact Support</Link>
              </Button>
              <Button variant="ghost" asChild>
                <Link to="/faq">Visit FAQ</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};