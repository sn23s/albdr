import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Plus, 
  Edit, 
  Trash2, 
  User, 
  Search, 
  Phone, 
  Calendar, 
  ShoppingBag, 
  DollarSign,
  Users,
  TrendingUp,
  Eye,
  Grid3X3,
  List,
  Star,
  Clock
} from 'lucide-react'

const CustomersPage = () => {
  const [customers, setCustomers] = useState([])
  const [filteredCustomers, setFilteredCustomers] = useState([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingCustomer, setEditingCustomer] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState('table') // 'table' or 'grid'
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    address: ''
  })

  const fetchCustomers = async () => {
    try {
      const response = await fetch('/api/customers')
      const data = await response.json()
      setCustomers(data)
      setFilteredCustomers(data)
    } catch (error) {
      console.error('Error fetching customers:', error)
      // Mock data for demonstration
      const mockData = [
        {
          id: 1,
          name: 'أحمد محمد علي',
          phone: '07901234567',
          email: 'ahmed@example.com',
          address: 'بغداد - الكرادة',
          created_at: '2024-01-15',
          total_purchases: 5,
          total_spent: 1250.00,
          last_purchase: '2024-06-20',
          loyalty_points: 125,
          status: 'active'
        },
        {
          id: 2,
          name: 'فاطمة حسن',
          phone: '07801234567',
          email: 'fatima@example.com',
          address: 'بغداد - الجادرية',
          created_at: '2024-02-10',
          total_purchases: 3,
          total_spent: 750.00,
          last_purchase: '2024-06-15',
          loyalty_points: 75,
          status: 'active'
        },
        {
          id: 3,
          name: 'محمد حسين',
          phone: '07701234567',
          email: 'mohammed@example.com',
          address: 'بغداد - المنصور',
          created_at: '2024-03-05',
          total_purchases: 1,
          total_spent: 150.00,
          last_purchase: '2024-03-05',
          loyalty_points: 15,
          status: 'inactive'
        }
      ]
      setCustomers(mockData)
      setFilteredCustomers(mockData)
    }
  }

  useEffect(() => {
    fetchCustomers()
  }, [])

  useEffect(() => {
    const filtered = customers.filter(customer => 
      customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      customer.phone.includes(searchTerm) ||
      (customer.email && customer.email.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    setFilteredCustomers(filtered)
  }, [searchTerm, customers])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const url = editingCustomer ? `/api/customers/${editingCustomer.id}` : '/api/customers'
      const method = editingCustomer ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        fetchCustomers()
        setIsDialogOpen(false)
        resetForm()
      }
    } catch (error) {
      console.error('Error saving customer:', error)
    }
  }

  const handleEdit = (customer) => {
    setEditingCustomer(customer)
    setFormData({
      name: customer.name,
      phone: customer.phone || '',
      email: customer.email || '',
      address: customer.address || ''
    })
    setIsDialogOpen(true)
  }

  const handleDelete = async (id) => {
    if (confirm('هل أنت متأكد من حذف هذا الزبون؟')) {
      try {
        const response = await fetch(`/api/customers/${id}`, {
          method: 'DELETE',
        })
        if (response.ok) {
          fetchCustomers()
        }
      } catch (error) {
        console.error('Error deleting customer:', error)
      }
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      phone: '',
      email: '',
      address: ''
    })
    setEditingCustomer(null)
  }

  const getCustomerStatus = (customer) => {
    const daysSinceLastPurchase = Math.floor((new Date() - new Date(customer.last_purchase)) / (1000 * 60 * 60 * 24))
    if (daysSinceLastPurchase <= 30) return { status: 'active', color: 'bg-green-500', text: 'نشط' }
    if (daysSinceLastPurchase <= 90) return { status: 'moderate', color: 'bg-yellow-500', text: 'متوسط' }
    return { status: 'inactive', color: 'bg-red-500', text: 'غير نشط' }
  }

  const getLoyaltyLevel = (points) => {
    if (points >= 100) return { level: 'gold', color: 'bg-yellow-500', text: 'ذهبي' }
    if (points >= 50) return { level: 'silver', color: 'bg-gray-400', text: 'فضي' }
    return { level: 'bronze', color: 'bg-orange-500', text: 'برونزي' }
  }

  const CustomerCard = ({ customer }) => {
    const status = getCustomerStatus(customer)
    const loyalty = getLoyaltyLevel(customer.loyalty_points)
    
    return (
      <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <User className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-lg">{customer.name}</CardTitle>
                <CardDescription className="flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  {customer.phone}
                </CardDescription>
              </div>
            </div>
            <div className="flex gap-2">
              <Badge className={`${status.color} text-white`}>
                {status.text}
              </Badge>
              <Badge className={`${loyalty.color} text-white`}>
                {loyalty.text}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">إجمالي المشتريات</div>
                <div className="font-bold text-green-600">
                  ${customer.total_spent.toLocaleString()}
                </div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">عدد المشتريات</div>
                <div className="font-bold text-purple-600">
                  {customer.total_purchases}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between items-center text-sm">
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4 text-gray-500" />
                <span>آخر شراء: {new Date(customer.last_purchase).toLocaleDateString('ar-EG')}</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-500" />
                <span>{customer.loyalty_points} نقطة</span>
              </div>
            </div>
            
            {customer.address && (
              <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                📍 {customer.address}
              </div>
            )}
            
            <div className="flex gap-2 pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleEdit(customer)}
                className="flex-1"
              >
                <Edit className="h-4 w-4 mr-1" />
                تعديل
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
              >
                <Eye className="h-4 w-4 mr-1" />
                عرض
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleDelete(customer.id)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const stats = {
    total: customers.length,
    active: customers.filter(c => getCustomerStatus(c).status === 'active').length,
    totalSpent: customers.reduce((sum, c) => sum + c.total_spent, 0),
    avgSpent: customers.length > 0 ? customers.reduce((sum, c) => sum + c.total_spent, 0) / customers.length : 0
  }

  return (
    <div className="space-y-6 p-6">
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-full">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-gray-600">إجمالي الزبائن</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-full">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">{stats.active}</div>
                <div className="text-sm text-gray-600">زبائن نشطون</div>
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
                <div className="text-2xl font-bold">${stats.totalSpent.toLocaleString()}</div>
                <div className="text-sm text-gray-600">إجمالي المبيعات</div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-full">
                <ShoppingBag className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold">${stats.avgSpent.toFixed(0)}</div>
                <div className="text-sm text-gray-600">متوسط الإنفاق</div>
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
                <Users className="h-5 w-5" />
                إدارة الزبائن
              </CardTitle>
              <CardDescription>إضافة وتعديل وحذف الزبائن</CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button onClick={resetForm} className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                  <Plus className="mr-2 h-4 w-4" />
                  إضافة زبون جديد
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]" dir="rtl">
                <DialogHeader>
                  <DialogTitle>{editingCustomer ? 'تعديل الزبون' : 'إضافة زبون جديد'}</DialogTitle>
                  <DialogDescription>
                    {editingCustomer ? 'تعديل بيانات الزبون' : 'أدخل بيانات الزبون الجديد'}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit}>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="name" className="text-right">
                        اسم الزبون
                      </Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        className="col-span-3"
                        required
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="phone" className="text-right">
                        رقم الهاتف
                      </Label>
                      <Input
                        id="phone"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        className="col-span-3"
                        placeholder="اختياري"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="email" className="text-right">
                        البريد الإلكتروني
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        className="col-span-3"
                        placeholder="اختياري"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="address" className="text-right">
                        العنوان
                      </Label>
                      <Input
                        id="address"
                        value={formData.address}
                        onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                        className="col-span-3"
                        placeholder="اختياري"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="submit">{editingCustomer ? 'تحديث' : 'إضافة'}</Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {/* Search and View Mode */}
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="البحث في الزبائن..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant={viewMode === 'table' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('table')}
              >
                <List className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3X3 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Customers Display */}
          {viewMode === 'grid' ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filteredCustomers.map((customer) => (
                <CustomerCard key={customer.id} customer={customer} />
              ))}
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-right">اسم الزبون</TableHead>
                  <TableHead className="text-right">رقم الهاتف</TableHead>
                  <TableHead className="text-right">البريد الإلكتروني</TableHead>
                  <TableHead className="text-right">إجمالي المشتريات</TableHead>
                  <TableHead className="text-right">آخر شراء</TableHead>
                  <TableHead className="text-right">الحالة</TableHead>
                  <TableHead className="text-right">المستوى</TableHead>
                  <TableHead className="text-right">الإجراءات</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredCustomers.map((customer) => {
                  const status = getCustomerStatus(customer)
                  const loyalty = getLoyaltyLevel(customer.loyalty_points)
                  
                  return (
                    <TableRow key={customer.id} className="hover:bg-gray-50">
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4" />
                          {customer.name}
                        </div>
                      </TableCell>
                      <TableCell>{customer.phone || 'غير محدد'}</TableCell>
                      <TableCell>{customer.email || 'غير محدد'}</TableCell>
                      <TableCell>${customer.total_spent.toLocaleString()}</TableCell>
                      <TableCell>{new Date(customer.last_purchase).toLocaleDateString('ar-EG')}</TableCell>
                      <TableCell>
                        <Badge className={`${status.color} text-white`}>
                          {status.text}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`${loyalty.color} text-white`}>
                          {loyalty.text}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEdit(customer)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDelete(customer.id)}
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
          )}
          
          {filteredCustomers.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>لا توجد زبائن تطابق البحث</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default CustomersPage

