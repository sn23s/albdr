import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Plus, 
  Edit, 
  Trash2, 
  ShoppingCart, 
  Printer, 
  QrCode, 
  Search, 
  Filter, 
  Calendar,
  DollarSign,
  TrendingUp,
  Package,
  Users,
  Eye,
  Calculator,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import QRScanner from './QRScanner'
import InvoicePrint from './InvoicePrint'

const SalesPage = () => {
  const [sales, setSales] = useState([])
  const [filteredSales, setFilteredSales] = useState([])
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isQRScannerOpen, setIsQRScannerOpen] = useState(false)
  const [isInvoicePrintOpen, setIsInvoicePrintOpen] = useState(false)
  const [selectedSale, setSelectedSale] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterPeriod, setFilterPeriod] = useState('all')
  const [filterCurrency, setFilterCurrency] = useState('all')
  const [saleItems, setSaleItems] = useState([{ product_id: '', quantity: 1, price: 0, warranty_months: 0 }])
  const [formData, setFormData] = useState({
    customer_id: '',
    currency: 'IQD'
  })

  const fetchSales = async () => {
    try {
      const response = await fetch('/api/sales')
      const data = await response.json()
      setSales(data)
      setFilteredSales(data)
    } catch (error) {
      console.error('Error fetching sales:', error)
      // Mock data for demonstration
      const mockData = [
        {
          id: 1,
          customer_id: 1,
          sale_date: '2024-06-20T10:30:00',
          total_amount: 250.00,
          currency: 'USD',
          status: 'completed',
          items: [
            { product_name: 'مصباح LED 20 واط', quantity: 2, price: 25.00 },
            { product_name: 'ثريا كريستال', quantity: 1, price: 200.00 }
          ]
        },
        {
          id: 2,
          customer_id: 2,
          sale_date: '2024-06-19T14:15:00',
          total_amount: 150.00,
          currency: 'USD',
          status: 'completed',
          items: [
            { product_name: 'مصباح فلورسنت 40 واط', quantity: 10, price: 15.00 }
          ]
        },
        {
          id: 3,
          customer_id: null,
          sale_date: '2024-06-18T09:45:00',
          total_amount: 75000,
          currency: 'IQD',
          status: 'pending',
          items: [
            { product_name: 'مصباح LED 20 واط', quantity: 3, price: 25000 }
          ]
        }
      ]
      setSales(mockData)
      setFilteredSales(mockData)
    }
  }

  const fetchProducts = async () => {
    try {
      const response = await fetch('/api/products')
      const data = await response.json()
      setProducts(data)
    } catch (error) {
      console.error('Error fetching products:', error)
      // Mock data
      const mockProducts = [
        { id: 1, name: 'مصباح LED 20 واط', selling_price: 25.00, quantity: 50, currency: 'USD' },
        { id: 2, name: 'مصباح فلورسنت 40 واط', selling_price: 15.00, quantity: 5, currency: 'USD' },
        { id: 3, name: 'ثريا كريستال', selling_price: 250000, quantity: 3, currency: 'IQD' }
      ]
      setProducts(mockProducts)
    }
  }

  const fetchCustomers = async () => {
    try {
      const response = await fetch('/api/customers')
      const data = await response.json()
      setCustomers(data)
    } catch (error) {
      console.error('Error fetching customers:', error)
      // Mock data
      const mockCustomers = [
        { id: 1, name: 'أحمد محمد علي', phone: '07901234567' },
        { id: 2, name: 'فاطمة حسن', phone: '07801234567' },
        { id: 3, name: 'محمد حسين', phone: '07701234567' }
      ]
      setCustomers(mockCustomers)
    }
  }

  useEffect(() => {
    fetchSales()
    fetchProducts()
    fetchCustomers()
  }, [])

  useEffect(() => {
    let filtered = sales.filter(sale => {
      const matchesSearch = sale.id.toString().includes(searchTerm) ||
                           (sale.customer_id && customers.find(c => c.id === sale.customer_id)?.name.toLowerCase().includes(searchTerm.toLowerCase()))
      
      const matchesCurrency = filterCurrency === 'all' || sale.currency === filterCurrency
      
      let matchesPeriod = true
      if (filterPeriod !== 'all') {
        const saleDate = new Date(sale.sale_date)
        const now = new Date()
        const daysDiff = Math.floor((now - saleDate) / (1000 * 60 * 60 * 24))
        
        switch (filterPeriod) {
          case 'today':
            matchesPeriod = daysDiff === 0
            break
          case 'week':
            matchesPeriod = daysDiff <= 7
            break
          case 'month':
            matchesPeriod = daysDiff <= 30
            break
        }
      }
      
      return matchesSearch && matchesCurrency && matchesPeriod
    })
    setFilteredSales(filtered)
  }, [searchTerm, filterCurrency, filterPeriod, sales, customers])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const totalAmount = saleItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
    
    try {
      const response = await fetch('/api/sales', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          customer_id: formData.customer_id || null,
          total_amount: totalAmount,
          items: saleItems.filter(item => item.product_id && item.quantity > 0)
        }),
      })

      if (response.ok) {
        fetchSales()
        fetchProducts()
        setIsDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error('Error saving sale:', error)
    }
  }

  const handleDelete = async (id) => {
    if (confirm('هل أنت متأكد من حذف هذه المبيعة؟')) {
      try {
        const response = await fetch(`/api/sales/${id}`, {
          method: 'DELETE',
        })
        if (response.ok) {
          fetchSales()
          fetchProducts()
        }
      } catch (error) {
        console.error('Error deleting sale:', error)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      customer_id: '',
      currency: 'IQD'
    })
    setSaleItems([{ product_id: '', quantity: 1, price: 0, warranty_months: 0 }])
  }

  const addSaleItem = () => {
    setSaleItems([...saleItems, { product_id: '', quantity: 1, price: 0, warranty_months: 0 }])
  }

  const removeSaleItem = (index) => {
    setSaleItems(saleItems.filter((_, i) => i !== index))
  }

  const updateSaleItem = (index, field, value) => {
    const updatedItems = [...saleItems]
    updatedItems[index][field] = value
    
    if (field === 'product_id') {
      const product = products.find(p => p.id === parseInt(value))
      if (product) {
        updatedItems[index].price = product.selling_price
      }
    }
    
    setSaleItems(updatedItems)
  }

  const getTotalAmount = () => {
    return saleItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  }

  const printInvoice = (sale) => {
    setSelectedSale(sale)
    setIsInvoicePrintOpen(true)
  }

  const handleQRScan = async (qrCode) => {
    try {
      const response = await fetch(`/api/products/qr/${qrCode}`)
      if (response.ok) {
        const product = await response.json()
        
        const existingItemIndex = saleItems.findIndex(item => item.product_id === product.id.toString())
        
        if (existingItemIndex >= 0) {
          const updatedItems = [...saleItems]
          updatedItems[existingItemIndex].quantity += 1
          setSaleItems(updatedItems)
        } else {
          setSaleItems([...saleItems, {
            product_id: product.id.toString(),
            quantity: 1,
            price: product.selling_price,
            warranty_months: 0
          }])
        }
        
        if (!isDialogOpen) {
          setIsDialogOpen(true)
        }
      } else {
        alert('لم يتم العثور على منتج بهذا الرمز')
      }
    } catch (error) {
      console.error('Error fetching product by QR:', error)
      alert('خطأ في البحث عن المنتج')
    }
  }

  const getSaleStatus = (sale) => {
    if (sale.status === 'completed') return { color: 'bg-green-500', text: 'مكتملة' }
    if (sale.status === 'pending') return { color: 'bg-yellow-500', text: 'معلقة' }
    return { color: 'bg-red-500', text: 'ملغية' }
  }

  const stats = {
    totalSales: sales.length,
    todaySales: sales.filter(s => {
      const today = new Date().toDateString()
      return new Date(s.sale_date).toDateString() === today
    }).length,
    totalRevenue: sales.reduce((sum, s) => {
      // Convert to USD for unified calculation
      const amount = s.currency === 'USD' ? s.total_amount : s.total_amount / 1500
      return sum + amount
    }, 0),
    avgSaleValue: sales.length > 0 ? sales.reduce((sum, s) => {
      const amount = s.currency === 'USD' ? s.total_amount : s.total_amount / 1500
      return sum + amount
    }, 0) / sales.length : 0
  }

  return (
    <div className="space-y-6 p-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <ShoppingCart className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.totalSales}</div>
                <div className="text-sm text-gray-600">إجمالي المبيعات</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-full">
                <Calendar className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.todaySales}</div>
                <div className="text-sm text-gray-600">مبيعات اليوم</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-full">
                <DollarSign className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">${stats.totalRevenue.toFixed(0)}</div>
                <div className="text-sm text-gray-600">إجمالي الإيرادات</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-full">
                <TrendingUp className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">${stats.avgSaleValue.toFixed(0)}</div>
                <div className="text-sm text-gray-600">متوسط قيمة المبيعة</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="flex items-center gap-2">
                <ShoppingCart className="h-5 w-5" />
                إدارة المبيعات
              </CardTitle>
              <CardDescription>إضافة وإدارة المبيعات والفواتير</CardDescription>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setIsQRScannerOpen(true)} variant="outline" className="bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white border-0">
                <QrCode className="mr-2 h-4 w-4" />
                مسح QR
              </Button>
              <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                <DialogTrigger asChild>
                  <Button onClick={resetForm} className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                    <Plus className="mr-2 h-4 w-4" />
                    إضافة مبيعة جديدة
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto" dir="rtl">
                  <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                      <ShoppingCart className="h-5 w-5" />
                      إضافة مبيعة جديدة
                    </DialogTitle>
                    <DialogDescription>
                      أدخل بيانات المبيعة الجديدة وحدد المنتجات
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit}>
                    <div className="grid gap-6 py-4">
                      {/* Customer and Currency Selection */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="customer" className="text-right font-medium">
                            الزبون
                          </Label>
                          <Select value={formData.customer_id} onValueChange={(value) => setFormData({ ...formData, customer_id: value })}>
                            <SelectTrigger>
                              <SelectValue placeholder="اختر الزبون (اختياري)" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="">بدون زبون</SelectItem>
                              {customers.map((customer) => (
                                <SelectItem key={customer.id} value={customer.id.toString()}>
                                  {customer.name} - {customer.phone}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="currency" className="text-right font-medium">
                            العملة
                          </Label>
                          <Select value={formData.currency} onValueChange={(value) => setFormData({ ...formData, currency: value })}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="IQD">دينار عراقي</SelectItem>
                              <SelectItem value="USD">دولار أمريكي</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      {/* Products Section */}
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <Label className="text-right font-medium flex items-center gap-2">
                            <Package className="h-4 w-4" />
                            المنتجات
                          </Label>
                          <Button type="button" onClick={addSaleItem} size="sm" variant="outline">
                            <Plus className="h-4 w-4 mr-1" />
                            إضافة منتج
                          </Button>
                        </div>
                        
                        <div className="space-y-3">
                          {saleItems.map((item, index) => (
                            <Card key={index} className="p-4">
                              <div className="grid grid-cols-12 gap-3 items-center">
                                <div className="col-span-4">
                                  <Label className="text-xs text-gray-600">المنتج</Label>
                                  <Select 
                                    value={item.product_id.toString()} 
                                    onValueChange={(value) => updateSaleItem(index, 'product_id', value)}
                                  >
                                    <SelectTrigger>
                                      <SelectValue placeholder="اختر المنتج" />
                                    </SelectTrigger>
                                    <SelectContent>
                                      {products.map((product) => (
                                        <SelectItem key={product.id} value={product.id.toString()}>
                                          {product.name} (متوفر: {product.quantity})
                                        </SelectItem>
                                      ))}
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div className="col-span-2">
                                  <Label className="text-xs text-gray-600">الكمية</Label>
                                  <Input
                                    type="number"
                                    placeholder="الكمية"
                                    value={item.quantity}
                                    onChange={(e) => updateSaleItem(index, 'quantity', parseInt(e.target.value) || 0)}
                                    min="1"
                                  />
                                </div>
                                <div className="col-span-2">
                                  <Label className="text-xs text-gray-600">السعر</Label>
                                  <Input
                                    type="number"
                                    step="0.01"
                                    placeholder="السعر"
                                    value={item.price}
                                    onChange={(e) => updateSaleItem(index, 'price', parseFloat(e.target.value) || 0)}
                                  />
                                </div>
                                <div className="col-span-2">
                                  <Label className="text-xs text-gray-600">الضمان (شهر)</Label>
                                  <Input
                                    type="number"
                                    placeholder="الضمان"
                                    value={item.warranty_months}
                                    onChange={(e) => updateSaleItem(index, 'warranty_months', parseInt(e.target.value) || 0)}
                                    min="0"
                                  />
                                </div>
                                <div className="col-span-1">
                                  <Label className="text-xs text-gray-600">المجموع</Label>
                                  <div className="text-sm font-bold text-green-600">
                                    {(item.price * item.quantity).toLocaleString()}
                                  </div>
                                </div>
                                <div className="col-span-1">
                                  <Button
                                    type="button"
                                    variant="destructive"
                                    size="sm"
                                    onClick={() => removeSaleItem(index)}
                                    disabled={saleItems.length === 1}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </div>
                              </div>
                            </Card>
                          ))}
                        </div>
                        
                        {/* Total */}
                        <Card className="p-4 bg-gradient-to-r from-green-50 to-blue-50">
                          <div className="flex justify-between items-center">
                            <div className="flex items-center gap-2">
                              <Calculator className="h-5 w-5 text-green-600" />
                              <span className="font-medium">المجموع الإجمالي:</span>
                            </div>
                            <div className="text-2xl font-bold text-green-600">
                              {getTotalAmount().toLocaleString()} {formData.currency}
                            </div>
                          </div>
                        </Card>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                        إلغاء
                      </Button>
                      <Button type="submit" className="bg-gradient-to-r from-green-500 to-blue-600 hover:from-green-600 hover:to-blue-700">
                        <CheckCircle className="h-4 w-4 mr-1" />
                        إضافة المبيعة
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Search and Filters */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="البحث في المبيعات..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={filterPeriod} onValueChange={setFilterPeriod}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="الفترة" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">جميع الفترات</SelectItem>
                <SelectItem value="today">اليوم</SelectItem>
                <SelectItem value="week">هذا الأسبوع</SelectItem>
                <SelectItem value="month">هذا الشهر</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filterCurrency} onValueChange={setFilterCurrency}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="العملة" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">جميع العملات</SelectItem>
                <SelectItem value="IQD">دينار عراقي</SelectItem>
                <SelectItem value="USD">دولار أمريكي</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Sales Table */}
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-right">رقم المبيعة</TableHead>
                <TableHead className="text-right">الزبون</TableHead>
                <TableHead className="text-right">تاريخ البيع</TableHead>
                <TableHead className="text-right">المبلغ الإجمالي</TableHead>
                <TableHead className="text-right">العملة</TableHead>
                <TableHead className="text-right">الحالة</TableHead>
                <TableHead className="text-right">عدد المنتجات</TableHead>
                <TableHead className="text-right">الإجراءات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSales.map((sale) => {
                const status = getSaleStatus(sale)
                const customer = customers.find(c => c.id === sale.customer_id)
                
                return (
                  <TableRow key={sale.id} className="hover:bg-gray-50">
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <ShoppingCart className="h-4 w-4 text-blue-500" />
                        #{sale.id}
                      </div>
                    </TableCell>
                    <TableCell>
                      {customer ? (
                        <div>
                          <div className="font-medium">{customer.name}</div>
                          <div className="text-sm text-gray-500">{customer.phone}</div>
                        </div>
                      ) : (
                        <span className="text-gray-500">زبون عادي</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4 text-gray-400" />
                        {new Date(sale.sale_date).toLocaleDateString('ar-EG')}
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(sale.sale_date).toLocaleTimeString('ar-EG', { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </div>
                    </TableCell>
                    <TableCell className="font-bold text-green-600">
                      {sale.total_amount.toLocaleString()}
                    </TableCell>
                    <TableCell>{sale.currency}</TableCell>
                    <TableCell>
                      <Badge className={`${status.color} text-white`}>
                        {status.text}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Package className="h-4 w-4 text-gray-400" />
                        {sale.items ? sale.items.length : 0}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => printInvoice(sale)}
                          title="طباعة الفاتورة"
                        >
                          <Printer className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          title="عرض التفاصيل"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDelete(sale.id)}
                          title="حذف المبيعة"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
          
          {filteredSales.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <ShoppingCart className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>لا توجد مبيعات تطابق البحث</p>
            </div>
          )}
        </CardContent>
      </Card>
      
      <QRScanner
        isOpen={isQRScannerOpen}
        onClose={() => setIsQRScannerOpen(false)}
        onScan={handleQRScan}
      />
      
      <InvoicePrint
        isOpen={isInvoicePrintOpen}
        onClose={() => setIsInvoicePrintOpen(false)}
        sale={selectedSale}
      />
    </div>
  )
}

export default SalesPage

