import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ShoppingCart, 
  Plus, 
  Minus, 
  Package, 
  Phone, 
  MapPin, 
  Truck, 
  Store,
  Star,
  Heart,
  Search,
  Filter,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const PublicStore = () => {
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [orderForm, setOrderForm] = useState({
    customer_name: '',
    customer_phone: '',
    customer_address: '',
    order_type: 'pickup',
    notes: ''
  });
  const [orderStatus, setOrderStatus] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/public/products');
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: Math.min(item.quantity + 1, product.quantity) }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity === 0) {
      removeFromCart(productId);
    } else {
      const product = products.find(p => p.id === productId);
      setCart(cart.map(item =>
        item.id === productId
          ? { ...item, quantity: Math.min(newQuantity, product.quantity) }
          : item
      ));
    }
  };

  const getTotalAmount = () => {
    return cart.reduce((total, item) => total + (item.selling_price * item.quantity), 0);
  };

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const submitOrder = async () => {
    if (!orderForm.customer_name || !orderForm.customer_phone) {
      alert('يرجى إدخال الاسم ورقم الهاتف');
      return;
    }

    if (cart.length === 0) {
      alert('السلة فارغة');
      return;
    }

    const orderData = {
      ...orderForm,
      total_amount: getTotalAmount(),
      currency: 'IQD',
      items: cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        price: item.selling_price
      }))
    };

    try {
      const response = await fetch('http://localhost:5001/api/public/order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      const result = await response.json();

      if (response.ok) {
        setOrderStatus({
          type: 'success',
          message: result.message,
          orderId: result.order_id
        });
        setCart([]);
        setOrderForm({
          customer_name: '',
          customer_phone: '',
          customer_address: '',
          order_type: 'pickup',
          notes: ''
        });
        setShowCheckout(false);
      } else {
        setOrderStatus({
          type: 'error',
          message: result.error || 'حدث خطأ في إرسال الطلب'
        });
      }
    } catch (error) {
      setOrderStatus({
        type: 'error',
        message: 'خطأ في الاتصال بالخادم'
      });
    }
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold">البدر</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">البدر للإنارة</h1>
                <p className="text-sm text-gray-600">متجر الإنارة والكهربائيات</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Button
                onClick={() => setShowCart(!showCart)}
                className="relative flex items-center gap-2"
              >
                <ShoppingCart className="w-4 h-4" />
                السلة
                {getTotalItems() > 0 && (
                  <Badge className="absolute -top-2 -right-2 bg-red-500 text-white text-xs">
                    {getTotalItems()}
                  </Badge>
                )}
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search */}
        <div className="mb-8">
          <div className="relative max-w-md mx-auto">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="البحث عن المنتجات..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white shadow-sm"
            />
          </div>
        </div>

        {/* Order Status */}
        {orderStatus && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            orderStatus.type === 'success' 
              ? 'bg-green-100 text-green-800 border border-green-200' 
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            {orderStatus.type === 'success' ? (
              <CheckCircle className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <div>
              <p className="font-medium">{orderStatus.message}</p>
              {orderStatus.orderId && (
                <p className="text-sm">رقم الطلب: #{orderStatus.orderId}</p>
              )}
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setOrderStatus(null)}
              className="mr-auto"
            >
              إغلاق
            </Button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Products */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map((product) => (
                <Card key={product.id} className="hover:shadow-xl transition-all duration-300 bg-white">
                  <CardContent className="p-0">
                    <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 rounded-t-lg flex items-center justify-center">
                      <Package className="w-16 h-16 text-gray-400" />
                    </div>
                    <div className="p-4">
                      <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">{product.description}</p>
                      
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <span className="text-2xl font-bold text-blue-600">
                            {product.selling_price.toLocaleString()}
                          </span>
                          <span className="text-gray-600 text-sm mr-1">{product.currency}</span>
                        </div>
                        <Badge className={product.quantity > 10 ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                          متوفر: {product.quantity}
                        </Badge>
                      </div>

                      <div className="flex items-center gap-2">
                        {cart.find(item => item.id === product.id) ? (
                          <div className="flex items-center gap-2 flex-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(product.id, cart.find(item => item.id === product.id).quantity - 1)}
                            >
                              <Minus className="w-4 h-4" />
                            </Button>
                            <span className="font-medium px-3">
                              {cart.find(item => item.id === product.id)?.quantity || 0}
                            </span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => updateQuantity(product.id, cart.find(item => item.id === product.id).quantity + 1)}
                              disabled={cart.find(item => item.id === product.id)?.quantity >= product.quantity}
                            >
                              <Plus className="w-4 h-4" />
                            </Button>
                          </div>
                        ) : (
                          <Button
                            onClick={() => addToCart(product)}
                            disabled={product.quantity === 0}
                            className="flex-1 flex items-center gap-2"
                          >
                            <Plus className="w-4 h-4" />
                            إضافة للسلة
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Cart Sidebar */}
          <div className={`lg:block ${showCart ? 'block' : 'hidden'}`}>
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5" />
                  سلة التسوق
                </CardTitle>
                <CardDescription>
                  {getTotalItems()} منتج - {getTotalAmount().toLocaleString()} IQD
                </CardDescription>
              </CardHeader>
              <CardContent>
                {cart.length === 0 ? (
                  <p className="text-gray-600 text-center py-8">السلة فارغة</p>
                ) : (
                  <div className="space-y-4">
                    {cart.map((item) => (
                      <div key={item.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{item.name}</h4>
                          <p className="text-gray-600 text-xs">
                            {item.selling_price.toLocaleString()} {item.currency}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          >
                            <Minus className="w-3 h-3" />
                          </Button>
                          <span className="text-sm font-medium px-2">{item.quantity}</span>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          >
                            <Plus className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    ))}

                    <div className="border-t pt-4">
                      <div className="flex justify-between items-center mb-4">
                        <span className="font-semibold">الإجمالي:</span>
                        <span className="font-bold text-lg text-blue-600">
                          {getTotalAmount().toLocaleString()} IQD
                        </span>
                      </div>

                      <Button
                        onClick={() => setShowCheckout(true)}
                        className="w-full"
                        disabled={cart.length === 0}
                      >
                        إتمام الطلب
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Checkout Modal */}
        {showCheckout && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>إتمام الطلب</CardTitle>
                <CardDescription>
                  يرجى إدخال بياناتك لإتمام الطلب
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">الاسم الكامل *</label>
                  <input
                    type="text"
                    value={orderForm.customer_name}
                    onChange={(e) => setOrderForm({...orderForm, customer_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="أدخل اسمك الكامل"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">رقم الهاتف *</label>
                  <input
                    type="tel"
                    value={orderForm.customer_phone}
                    onChange={(e) => setOrderForm({...orderForm, customer_phone: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="07xxxxxxxx"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">نوع الطلب</label>
                  <select
                    value={orderForm.order_type}
                    onChange={(e) => setOrderForm({...orderForm, order_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pickup">استلام من المحل</option>
                    <option value="delivery">توصيل</option>
                  </select>
                </div>

                {orderForm.order_type === 'delivery' && (
                  <div>
                    <label className="block text-sm font-medium mb-2">العنوان</label>
                    <textarea
                      value={orderForm.customer_address}
                      onChange={(e) => setOrderForm({...orderForm, customer_address: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="أدخل عنوانك بالتفصيل"
                      rows="3"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium mb-2">ملاحظات (اختياري)</label>
                  <textarea
                    value={orderForm.notes}
                    onChange={(e) => setOrderForm({...orderForm, notes: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="أي ملاحظات إضافية"
                    rows="2"
                  />
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="font-semibold">الإجمالي:</span>
                    <span className="font-bold text-lg text-blue-600">
                      {getTotalAmount().toLocaleString()} IQD
                    </span>
                  </div>
                </div>

                <div className="flex gap-3">
                  <Button
                    variant="outline"
                    onClick={() => setShowCheckout(false)}
                    className="flex-1"
                  >
                    إلغاء
                  </Button>
                  <Button
                    onClick={submitOrder}
                    className="flex-1"
                  >
                    تأكيد الطلب
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicStore;

