import { useState, useEffect, useRef } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { 
  Plus, 
  Edit, 
  Trash2, 
  QrCode, 
  Search, 
  Filter, 
  Package, 
  DollarSign, 
  AlertTriangle,
  Eye,
  Grid3X3,
  List,
  TrendingUp,
  TrendingDown,
  Upload,
  Image as ImageIcon,
  X,
  Camera,
  Star,
  ShoppingCart,
  BarChart3
} from 'lucide-react'

const ProductsPage = () => {
  const [products, setProducts] = useState([])
  const [stats, setStats] = useState({})
  const [categories, setCategories] = useState([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [isImageDialogOpen, setIsImageDialogOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCurrency, setFilterCurrency] = useState('all')
  const [filterStock, setFilterStock] = useState('all')
  const [filterCategory, setFilterCategory] = useState('all')
  const [viewMode, setViewMode] = useState('grid') // 'table' or 'grid'
  const [uploadingImage, setUploadingImage] = useState(false)
  const fileInputRef = useRef(null)
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    cost_price: '',
    selling_price: '',
    quantity: '',
    qr_code: '',
    currency: 'IQD',
    category: '',
    brand: '',
    model: '',
    color: '',
    size: '',
    weight: '',
    dimensions: '',
    min_stock_level: 5,
    max_stock_level: 100,
    reorder_point: 10,
    is_active: true,
    is_featured: false
  })

  useEffect(() => {
    fetchData()
  }, [])

  useEffect(() => {
    filterProducts()
  }, [products, searchTerm, filterCurrency, filterStock, filterCategory])

  const fetchData = async () => {
    try {
      const [productsRes, statsRes, categoriesRes] = await Promise.all([
        fetch('http://localhost:5001/api/products'),
        fetch('http://localhost:5001/api/products/stats'),
        fetch('http://localhost:5001/api/categories')
      ])

      const [productsData, statsData, categoriesData] = await Promise.all([
        productsRes.json(),
        statsRes.json(),
        categoriesRes.json()
      ])

      setProducts(productsData)
      setStats(statsData)
      setCategories(categoriesData)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  const filterProducts = () => {
    let filtered = products.filter(product => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.brand?.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesCurrency = filterCurrency === 'all' || product.currency === filterCurrency
      const matchesCategory = filterCategory === 'all' || product.category === filterCategory
      
      let matchesStock = true
      if (filterStock === 'low') {
        matchesStock = product.quantity <= product.min_stock_level
      } else if (filterStock === 'out') {
        matchesStock = product.quantity <= 0
      } else if (filterStock === 'available') {
        matchesStock = product.quantity > 0
      }
      
      return matchesSearch && matchesCurrency && matchesStock && matchesCategory
    })
    
    return filtered
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const url = editingProduct 
        ? `http://localhost:5001/api/products/${editingProduct.id}`
        : 'http://localhost:5001/api/products'
      
      const method = editingProduct ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        fetchData()
        resetForm()
        setIsDialogOpen(false)
      } else {
        alert('حدث خطأ في حفظ المنتج')
      }
    } catch (error) {
      console.error('Error saving product:', error)
      alert('حدث خطأ في الاتصال')
    }
  }

  const handleDelete = async (id) => {
    if (confirm('هل أنت متأكد من حذف هذا المنتج؟')) {
      try {
        const response = await fetch(`http://localhost:5001/api/products/${id}`, {
          method: 'DELETE',
        })

        if (response.ok) {
          fetchData()
        } else {
          alert('حدث خطأ في حذف المنتج')
        }
      } catch (error) {
        console.error('Error deleting product:', error)
        alert('حدث خطأ في الاتصال')
      }
    }
  }

  const handleImageUpload = async (file, isMain = false) => {
    if (!selectedProduct) return

    setUploadingImage(true)
    
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('is_main', isMain.toString())

      const response = await fetch(`http://localhost:5001/api/products/${selectedProduct.id}/upload-image`, {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        alert(result.message)
        fetchData()
        
        // Update selected product
        setSelectedProduct(result.product)
      } else {
        const error = await response.json()
        alert(error.error || 'حدث خطأ في رفع الصورة')
      }
    } catch (error) {
      console.error('Error uploading image:', error)
      alert('حدث خطأ في الاتصال')
    } finally {
      setUploadingImage(false)
    }
  }

  const handleRemoveImage = async (imagePath) => {
    if (!selectedProduct) return

    try {
      const response = await fetch(`http://localhost:5001/api/products/${selectedProduct.id}/remove-image`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image_path: imagePath }),
      })

      if (response.ok) {
        const result = await response.json()
        alert(result.message)
        fetchData()
        
        // Update selected product
        setSelectedProduct(result.product)
      } else {
        const error = await response.json()
        alert(error.error || 'حدث خطأ في حذف الصورة')
      }
    } catch (error) {
      console.error('Error removing image:', error)
      alert('حدث خطأ في الاتصال')
    }
  }

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      cost_price: '',
      selling_price: '',
      quantity: '',
      qr_code: '',
      currency: 'IQD',
      category: '',
      brand: '',
      model: '',
      color: '',
      size: '',
      weight: '',
      dimensions: '',
      min_stock_level: 5,
      max_stock_level: 100,
      reorder_point: 10,
      is_active: true,
      is_featured: false
    })
    setEditingProduct(null)
  }

  const openEditDialog = (product) => {
    setFormData({
      name: product.name,
      description: product.description || '',
      cost_price: product.cost_price,
      selling_price: product.selling_price,
      quantity: product.quantity,
      qr_code: product.qr_code || '',
      currency: product.currency,
      category: product.category || '',
      brand: product.brand || '',
      model: product.model || '',
      color: product.color || '',
      size: product.size || '',
      weight: product.weight || '',
      dimensions: product.dimensions || '',
      min_stock_level: product.min_stock_level || 5,
      max_stock_level: product.max_stock_level || 100,
      reorder_point: product.reorder_point || 10,
      is_active: product.is_active,
      is_featured: product.is_featured
    })
    setEditingProduct(product)
    setIsDialogOpen(true)
  }

  const openImageDialog = (product) => {
    setSelectedProduct(product)
    setIsImageDialogOpen(true)
  }

  const getStockBadgeColor = (product) => {
    if (product.quantity <= 0) return 'bg-red-100 text-red-800'
    if (product.quantity <= product.min_stock_level) return 'bg-yellow-100 text-yellow-800'
    return 'bg-green-100 text-green-800'
  }

  const getStockIcon = (product) => {
    if (product.quantity <= 0) return <AlertTriangle className="w-4 h-4" />
    if (product.quantity <= product.min_stock_level) return <TrendingDown className="w-4 h-4" />
    return <TrendingUp className="w-4 h-4" />
  }

  const filteredProducts = filterProducts()

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Package className="w-8 h-8 text-blue-600" />
            إدارة المنتجات
          </h1>
          <p className="text-gray-600 mt-1">إدارة شاملة للمنتجات مع الصور والتفاصيل</p>
        </div>
        <div className="flex gap-3">
          <div className="flex bg-gray-100 rounded-lg p-1">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'table' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('table')}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
          <Button onClick={() => setIsDialogOpen(true)} className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            منتج جديد
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">إجمالي المنتجات</p>
                <p className="text-3xl font-bold">{stats.total_products || 0}</p>
              </div>
              <Package className="w-12 h-12 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">قيمة المخزون</p>
                <p className="text-3xl font-bold">{(stats.total_selling_value || 0).toLocaleString()}</p>
              </div>
              <DollarSign className="w-12 h-12 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100">مخزون قليل</p>
                <p className="text-3xl font-bold">{stats.low_stock_products || 0}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-yellow-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100">ربح متوقع</p>
                <p className="text-3xl font-bold">{(stats.potential_profit || 0).toLocaleString()}</p>
              </div>
              <BarChart3 className="w-12 h-12 text-purple-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="البحث بالاسم، الوصف، أو العلامة التجارية..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">جميع الفئات</option>
              {categories.map(category => (
                <option key={category.id} value={category.name}>{category.name}</option>
              ))}
            </select>

            <select
              value={filterStock}
              onChange={(e) => setFilterStock(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">جميع المخزون</option>
              <option value="available">متوفر</option>
              <option value="low">مخزون قليل</option>
              <option value="out">نفد المخزون</option>
            </select>

            <select
              value={filterCurrency}
              onChange={(e) => setFilterCurrency(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">جميع العملات</option>
              <option value="IQD">دينار عراقي</option>
              <option value="USD">دولار أمريكي</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Products Display */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="relative">
                {product.main_image ? (
                  <img
                    src={`http://localhost:5001/api/uploads/${product.main_image}`}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                    <ImageIcon className="w-16 h-16 text-gray-400" />
                  </div>
                )}
                
                {product.is_featured && (
                  <div className="absolute top-2 right-2">
                    <Badge className="bg-yellow-500 text-white">
                      <Star className="w-3 h-3 mr-1" />
                      مميز
                    </Badge>
                  </div>
                )}
                
                <div className="absolute top-2 left-2">
                  <Badge className={getStockBadgeColor(product)}>
                    <div className="flex items-center gap-1">
                      {getStockIcon(product)}
                      {product.quantity}
                    </div>
                  </Badge>
                </div>
              </div>
              
              <CardContent className="p-4">
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg truncate">{product.name}</h3>
                  {product.brand && (
                    <p className="text-sm text-gray-600">{product.brand}</p>
                  )}
                  {product.category && (
                    <Badge variant="outline" className="text-xs">{product.category}</Badge>
                  )}
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-bold text-green-600">
                        {product.selling_price.toLocaleString()} {product.currency}
                      </p>
                      <p className="text-sm text-gray-500">
                        ربح: {product.profit_margin}%
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openImageDialog(product)}
                      className="flex-1"
                    >
                      <Camera className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => openEditDialog(product)}
                      className="flex-1"
                    >
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(product.id)}
                      className="flex-1 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>قائمة المنتجات</CardTitle>
            <CardDescription>
              عرض {filteredProducts.length} من أصل {products.length} منتج
            </CardDescription>
          </CardHeader>
          <CardContent>
            {filteredProducts.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد منتجات</h3>
                <p className="text-gray-600">لم يتم العثور على منتجات تطابق المعايير المحددة.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-right py-3 px-4 font-medium text-gray-700">الصورة</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">المنتج</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">الفئة</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">السعر</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">الكمية</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">الربح</th>
                      <th className="text-right py-3 px-4 font-medium text-gray-700">الإجراءات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map((product) => (
                      <tr key={product.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">
                          {product.main_image ? (
                            <img
                              src={`http://localhost:5001/api/uploads/${product.main_image}`}
                              alt={product.name}
                              className="w-12 h-12 object-cover rounded-lg"
                            />
                          ) : (
                            <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                              <ImageIcon className="w-6 h-6 text-gray-400" />
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-medium flex items-center gap-2">
                              {product.name}
                              {product.is_featured && <Star className="w-4 h-4 text-yellow-500" />}
                            </div>
                            {product.brand && (
                              <div className="text-sm text-gray-600">{product.brand}</div>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          {product.category && (
                            <Badge variant="outline">{product.category}</Badge>
                          )}
                        </td>
                        <td className="py-3 px-4">
                          <div className="font-medium text-green-600">
                            {product.selling_price.toLocaleString()} {product.currency}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <Badge className={getStockBadgeColor(product)}>
                            <div className="flex items-center gap-1">
                              {getStockIcon(product)}
                              {product.quantity}
                            </div>
                          </Badge>
                        </td>
                        <td className="py-3 px-4">
                          <span className="text-sm font-medium">
                            {product.profit_margin}%
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openImageDialog(product)}
                            >
                              <Camera className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => openEditDialog(product)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDelete(product.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Add/Edit Product Dialog */}
      {isDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle>
                {editingProduct ? 'تعديل المنتج' : 'إضافة منتج جديد'}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">اسم المنتج *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">الفئة</label>
                    <select
                      value={formData.category}
                      onChange={(e) => setFormData({...formData, category: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">اختر الفئة</option>
                      {categories.map(category => (
                        <option key={category.id} value={category.name}>{category.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">العلامة التجارية</label>
                    <input
                      type="text"
                      value={formData.brand}
                      onChange={(e) => setFormData({...formData, brand: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">الموديل</label>
                    <input
                      type="text"
                      value={formData.model}
                      onChange={(e) => setFormData({...formData, model: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">سعر التكلفة *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.cost_price}
                      onChange={(e) => setFormData({...formData, cost_price: parseFloat(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">سعر البيع *</label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.selling_price}
                      onChange={(e) => setFormData({...formData, selling_price: parseFloat(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">الكمية *</label>
                    <input
                      type="number"
                      value={formData.quantity}
                      onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">العملة *</label>
                    <select
                      value={formData.currency}
                      onChange={(e) => setFormData({...formData, currency: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="IQD">دينار عراقي</option>
                      <option value="USD">دولار أمريكي</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">الحد الأدنى للمخزون</label>
                    <input
                      type="number"
                      value={formData.min_stock_level}
                      onChange={(e) => setFormData({...formData, min_stock_level: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">رمز QR</label>
                    <input
                      type="text"
                      value={formData.qr_code}
                      onChange={(e) => setFormData({...formData, qr_code: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">الوصف</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                      className="rounded"
                    />
                    <span className="text-sm">منتج نشط</span>
                  </label>

                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={formData.is_featured}
                      onChange={(e) => setFormData({...formData, is_featured: e.target.checked})}
                      className="rounded"
                    />
                    <span className="text-sm">منتج مميز</span>
                  </label>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsDialogOpen(false)
                      resetForm()
                    }}
                    className="flex-1"
                  >
                    إلغاء
                  </Button>
                  <Button type="submit" className="flex-1">
                    {editingProduct ? 'تحديث' : 'إضافة'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Image Management Dialog */}
      {isImageDialogOpen && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="w-5 h-5" />
                إدارة صور المنتج: {selectedProduct.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Upload Section */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => {
                    const file = e.target.files[0]
                    if (file) {
                      handleImageUpload(file, selectedProduct.images.length === 0)
                    }
                  }}
                  accept="image/*"
                  className="hidden"
                />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">رفع صورة جديدة</h3>
                <p className="text-gray-600 mb-4">اختر صورة بصيغة JPG, PNG, GIF أو WebP</p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingImage}
                  className="flex items-center gap-2"
                >
                  {uploadingImage ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      جاري الرفع...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      اختيار صورة
                    </>
                  )}
                </Button>
              </div>

              {/* Images Grid */}
              {selectedProduct.images && selectedProduct.images.length > 0 ? (
                <div>
                  <h3 className="text-lg font-medium mb-4">صور المنتج ({selectedProduct.images.length})</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {selectedProduct.images.map((imagePath, index) => (
                      <div key={index} className="relative group">
                        <img
                          src={`http://localhost:5001/api/uploads/${imagePath}`}
                          alt={`${selectedProduct.name} - ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg"
                        />
                        
                        {imagePath === selectedProduct.main_image && (
                          <div className="absolute top-2 left-2">
                            <Badge className="bg-blue-500 text-white text-xs">
                              رئيسية
                            </Badge>
                          </div>
                        )}
                        
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleRemoveImage(imagePath)}
                            className="w-8 h-8 p-0"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد صور</h3>
                  <p className="text-gray-600">لم يتم رفع أي صور لهذا المنتج بعد.</p>
                </div>
              )}

              <div className="flex justify-end">
                <Button
                  onClick={() => {
                    setIsImageDialogOpen(false)
                    setSelectedProduct(null)
                  }}
                >
                  إغلاق
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

export default ProductsPage

