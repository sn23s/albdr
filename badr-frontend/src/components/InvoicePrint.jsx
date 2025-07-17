import { useState, useEffect, useRef } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { 
  Printer, 
  Download, 
  Settings, 
  FileText, 
  Receipt, 
  CreditCard,
  Phone,
  MapPin,
  Calendar,
  Hash,
  User,
  Package,
  DollarSign,
  X,
  Check,
  Copy
} from 'lucide-react'

const InvoicePrint = ({ isOpen, onClose, sale }) => {
  const [saleDetails, setSaleDetails] = useState(null)
  const [customer, setCustomer] = useState(null)
  const [products, setProducts] = useState([])
  const [template, setTemplate] = useState('standard') // standard, thermal, minimal, detailed
  const [settings, setSettings] = useState({
    showLogo: true,
    showCustomerInfo: true,
    showItemDetails: true,
    showNotes: true,
    showWarranty: true,
    paperSize: 'A4', // A4, thermal_80mm, thermal_58mm
    fontSize: 'medium', // small, medium, large
    includeQR: false,
    includeBarcode: false
  })
  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const printRef = useRef(null)

  useEffect(() => {
    if (sale && isOpen) {
      fetchSaleDetails()
    }
  }, [sale, isOpen])

  const fetchSaleDetails = async () => {
    try {
      // Fetch sale details with items
      const saleResponse = await fetch(`http://localhost:5001/api/sales/${sale.id}`)
      const saleData = await saleResponse.json()
      setSaleDetails(saleData)

      // Fetch customer details if exists
      if (sale.customer_id) {
        const customerResponse = await fetch(`http://localhost:5001/api/customers/${sale.customer_id}`)
        const customerData = await customerResponse.json()
        setCustomer(customerData)
      }

      // Fetch all products to get names
      const productsResponse = await fetch('http://localhost:5001/api/products')
      const productsData = await productsResponse.json()
      setProducts(productsData)
    } catch (error) {
      console.error('Error fetching sale details:', error)
    }
  }

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId)
    return product ? product.name : 'منتج غير معروف'
  }

  const getProductDetails = (productId) => {
    const product = products.find(p => p.id === productId)
    return product || {}
  }

  const handlePrint = () => {
    const printContent = printRef.current
    const originalContents = document.body.innerHTML
    
    document.body.innerHTML = printContent.innerHTML
    window.print()
    document.body.innerHTML = originalContents
    window.location.reload()
  }

  const handleDownloadPDF = () => {
    // This would require a PDF generation library
    alert('ميزة تحميل PDF ستكون متاحة قريباً')
  }

  const copyInvoiceNumber = () => {
    navigator.clipboard.writeText(`INV-${sale.id}`)
    alert('تم نسخ رقم الفاتورة')
  }

  const getCurrentDate = () => {
    return new Date().toLocaleDateString('ar-IQ', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getTemplateStyles = () => {
    const baseStyles = {
      fontSize: settings.fontSize === 'small' ? '12px' : settings.fontSize === 'large' ? '16px' : '14px'
    }

    switch (settings.paperSize) {
      case 'thermal_80mm':
        return {
          ...baseStyles,
          width: '80mm',
          maxWidth: '80mm',
          margin: '0 auto',
          fontSize: '11px'
        }
      case 'thermal_58mm':
        return {
          ...baseStyles,
          width: '58mm',
          maxWidth: '58mm',
          margin: '0 auto',
          fontSize: '10px'
        }
      default:
        return {
          ...baseStyles,
          width: '210mm',
          maxWidth: '210mm',
          margin: '0 auto'
        }
    }
  }

  const renderStandardTemplate = () => (
    <div className="bg-white p-8" style={getTemplateStyles()}>
      {/* Header */}
      {settings.showLogo && (
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-blue-800 rounded-full flex items-center justify-center">
              <Package className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-blue-800">البدر للإنارة</h1>
              <p className="text-gray-600">محل متخصص في جميع أنواع الإنارة والكهربائيات</p>
            </div>
          </div>
          <div className="flex items-center justify-center gap-6 text-sm text-gray-600">
            <div className="flex items-center gap-1">
              <Phone className="w-4 h-4" />
              <span>07XX XXX XXXX</span>
            </div>
            <div className="flex items-center gap-1">
              <MapPin className="w-4 h-4" />
              <span>بغداد - العراق</span>
            </div>
          </div>
          <div className="border-b-2 border-blue-800 mt-4"></div>
        </div>
      )}

      {/* Invoice Info */}
      <div className="grid grid-cols-2 gap-8 mb-8">
        <div>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            معلومات الفاتورة
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-gray-500" />
              <span className="font-medium">رقم الفاتورة:</span>
              <span className="font-mono bg-gray-100 px-2 py-1 rounded">INV-{sale.id}</span>
              <Button
                size="sm"
                variant="ghost"
                onClick={copyInvoiceNumber}
                className="p-1 h-6 w-6"
              >
                <Copy className="w-3 h-3" />
              </Button>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="font-medium">تاريخ البيع:</span>
              <span>{new Date(sale.sale_date).toLocaleDateString('ar-IQ')}</span>
            </div>
            <div className="flex items-center gap-2">
              <Printer className="w-4 h-4 text-gray-500" />
              <span className="font-medium">تاريخ الطباعة:</span>
              <span>{getCurrentDate()}</span>
            </div>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-gray-500" />
              <span className="font-medium">العملة:</span>
              <Badge variant="outline">
                {sale.currency === 'IQD' ? 'دينار عراقي' : 'دولار أمريكي'}
              </Badge>
            </div>
          </div>
        </div>

        {settings.showCustomerInfo && (
          <div>
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-green-600" />
              معلومات الزبون
            </h3>
            <div className="space-y-3">
              {customer ? (
                <>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-500" />
                    <span className="font-medium">الاسم:</span>
                    <span>{customer.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-500" />
                    <span className="font-medium">الهاتف:</span>
                    <span>{customer.phone || 'غير محدد'}</span>
                  </div>
                  {customer.email && (
                    <div className="flex items-center gap-2">
                      <span className="font-medium">البريد:</span>
                      <span>{customer.email}</span>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-gray-600 bg-gray-50 p-3 rounded">
                  <User className="w-5 h-5 inline mr-2" />
                  زبون عادي - بيع مباشر
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Items Table */}
      {settings.showItemDetails && (
        <div className="mb-8">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <Package className="w-5 h-5 text-purple-600" />
            تفاصيل المنتجات
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border border-gray-300 rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <th className="border border-gray-300 p-4 text-right font-semibold">#</th>
                  <th className="border border-gray-300 p-4 text-right font-semibold">المنتج</th>
                  <th className="border border-gray-300 p-4 text-center font-semibold">الكمية</th>
                  <th className="border border-gray-300 p-4 text-center font-semibold">السعر</th>
                  <th className="border border-gray-300 p-4 text-center font-semibold">المجموع</th>
                </tr>
              </thead>
              <tbody>
                {saleDetails?.items?.map((item, index) => {
                  const product = getProductDetails(item.product_id)
                  return (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="border border-gray-300 p-4 text-center font-medium">
                        {index + 1}
                      </td>
                      <td className="border border-gray-300 p-4">
                        <div>
                          <div className="font-medium">{getProductName(item.product_id)}</div>
                          {product.brand && (
                            <div className="text-sm text-gray-600">العلامة: {product.brand}</div>
                          )}
                          {product.model && (
                            <div className="text-sm text-gray-600">الموديل: {product.model}</div>
                          )}
                        </div>
                      </td>
                      <td className="border border-gray-300 p-4 text-center font-medium">
                        {item.quantity}
                      </td>
                      <td className="border border-gray-300 p-4 text-center">
                        {item.price.toLocaleString()} {sale.currency}
                      </td>
                      <td className="border border-gray-300 p-4 text-center font-bold text-green-600">
                        {(item.price * item.quantity).toLocaleString()} {sale.currency}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Summary */}
      <div className="mb-8">
        <div className="flex justify-end">
          <div className="w-80">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg border-2 border-blue-200">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">عدد الأصناف:</span>
                  <span>{saleDetails?.items?.length || 0}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-medium">إجمالي الكمية:</span>
                  <span>{saleDetails?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0}</span>
                </div>
                <div className="border-t border-blue-300 pt-3">
                  <div className="flex justify-between items-center text-xl font-bold text-blue-800">
                    <span>المبلغ الإجمالي:</span>
                    <span>{sale.total_amount.toLocaleString()} {sale.currency}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Warranty Info */}
      {settings.showWarranty && (
        <div className="mb-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-bold text-yellow-800 mb-2 flex items-center gap-2">
            <Check className="w-5 h-5" />
            معلومات الضمان
          </h4>
          <div className="text-sm text-yellow-700 space-y-1">
            <p>• جميع المنتجات مضمونة حسب ضمان الشركة المصنعة</p>
            <p>• يرجى الاحتفاظ بهذه الفاتورة كإثبات للشراء</p>
            <p>• للاستفسارات حول الضمان يرجى الاتصال بنا</p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center border-t-2 border-gray-200 pt-6">
        <div className="mb-4">
          <h4 className="font-bold text-lg text-blue-800 mb-2">شكراً لتعاملكم معنا</h4>
          <p className="text-gray-600">البدر للإنارة - جودة عالية وخدمة متميزة</p>
        </div>
        
        {settings.includeQR && (
          <div className="flex justify-center mb-4">
            <div className="w-24 h-24 bg-gray-200 border-2 border-dashed border-gray-400 rounded flex items-center justify-center">
              <span className="text-xs text-gray-500">QR Code</span>
            </div>
          </div>
        )}
        
        <div className="text-xs text-gray-500">
          <p>تم إنشاء هذه الفاتورة إلكترونياً في {getCurrentDate()}</p>
          <p>نظام إدارة البدر للإنارة - الإصدار 1.0</p>
        </div>
      </div>
    </div>
  )

  const renderThermalTemplate = () => (
    <div className="bg-white p-2" style={getTemplateStyles()}>
      {/* Header */}
      <div className="text-center mb-4">
        <h1 className="text-lg font-bold">البدر للإنارة</h1>
        <p className="text-xs">محل الإنارة والكهربائيات</p>
        <p className="text-xs">07XX XXX XXXX</p>
        <div className="border-b border-gray-400 my-2"></div>
      </div>

      {/* Invoice Info */}
      <div className="mb-4 text-xs">
        <div className="flex justify-between">
          <span>فاتورة:</span>
          <span>#{sale.id}</span>
        </div>
        <div className="flex justify-between">
          <span>التاريخ:</span>
          <span>{new Date(sale.sale_date).toLocaleDateString('ar-IQ')}</span>
        </div>
        {customer && (
          <div className="flex justify-between">
            <span>الزبون:</span>
            <span>{customer.name}</span>
          </div>
        )}
        <div className="border-b border-gray-400 my-2"></div>
      </div>

      {/* Items */}
      <div className="mb-4">
        {saleDetails?.items?.map((item, index) => (
          <div key={index} className="mb-2 text-xs">
            <div className="font-medium">{getProductName(item.product_id)}</div>
            <div className="flex justify-between">
              <span>{item.quantity} × {item.price.toLocaleString()}</span>
              <span>{(item.price * item.quantity).toLocaleString()}</span>
            </div>
          </div>
        ))}
        <div className="border-b border-gray-400 my-2"></div>
      </div>

      {/* Total */}
      <div className="text-center mb-4">
        <div className="text-lg font-bold">
          المجموع: {sale.total_amount.toLocaleString()} {sale.currency}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-xs">
        <p>شكراً لتعاملكم معنا</p>
        <p>احتفظ بالفاتورة للضمان</p>
      </div>
    </div>
  )

  if (!saleDetails) {
    return null
  }

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-6xl max-h-[95vh] overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Receipt className="w-5 h-5" />
                  فاتورة رقم #{sale.id}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={onClose}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-0">
              <div className="flex">
                {/* Settings Panel */}
                {isSettingsOpen && (
                  <div className="w-80 border-r bg-gray-50 p-4 overflow-y-auto max-h-[70vh]">
                    <h3 className="font-bold mb-4">إعدادات الطباعة</h3>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">قالب الطباعة</label>
                        <select
                          value={template}
                          onChange={(e) => setTemplate(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        >
                          <option value="standard">قالب قياسي</option>
                          <option value="thermal">قالب حراري</option>
                          <option value="minimal">قالب مبسط</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">حجم الورق</label>
                        <select
                          value={settings.paperSize}
                          onChange={(e) => setSettings({...settings, paperSize: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        >
                          <option value="A4">A4 (210mm)</option>
                          <option value="thermal_80mm">حراري 80mm</option>
                          <option value="thermal_58mm">حراري 58mm</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">حجم الخط</label>
                        <select
                          value={settings.fontSize}
                          onChange={(e) => setSettings({...settings, fontSize: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        >
                          <option value="small">صغير</option>
                          <option value="medium">متوسط</option>
                          <option value="large">كبير</option>
                        </select>
                      </div>

                      <div className="space-y-2">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={settings.showLogo}
                            onChange={(e) => setSettings({...settings, showLogo: e.target.checked})}
                          />
                          <span className="text-sm">عرض الشعار</span>
                        </label>

                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={settings.showCustomerInfo}
                            onChange={(e) => setSettings({...settings, showCustomerInfo: e.target.checked})}
                          />
                          <span className="text-sm">معلومات الزبون</span>
                        </label>

                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={settings.showItemDetails}
                            onChange={(e) => setSettings({...settings, showItemDetails: e.target.checked})}
                          />
                          <span className="text-sm">تفاصيل المنتجات</span>
                        </label>

                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={settings.showWarranty}
                            onChange={(e) => setSettings({...settings, showWarranty: e.target.checked})}
                          />
                          <span className="text-sm">معلومات الضمان</span>
                        </label>

                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={settings.includeQR}
                            onChange={(e) => setSettings({...settings, includeQR: e.target.checked})}
                          />
                          <span className="text-sm">رمز QR</span>
                        </label>
                      </div>
                    </div>
                  </div>
                )}

                {/* Preview */}
                <div className="flex-1 overflow-y-auto max-h-[70vh] bg-gray-100 p-4">
                  <div ref={printRef}>
                    {template === 'thermal' || settings.paperSize.includes('thermal') 
                      ? renderThermalTemplate() 
                      : renderStandardTemplate()
                    }
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="border-t p-4 flex justify-between items-center">
                <div className="flex gap-2">
                  <Button variant="outline" onClick={onClose}>
                    إغلاق
                  </Button>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleDownloadPDF}>
                    <Download className="w-4 h-4 mr-2" />
                    تحميل PDF
                  </Button>
                  <Button onClick={handlePrint}>
                    <Printer className="w-4 h-4 mr-2" />
                    طباعة
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          
          .print-content, .print-content * {
            visibility: visible;
          }
          
          .print-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            background: white;
          }
          
          @page {
            margin: 0;
            size: ${settings.paperSize === 'thermal_80mm' ? '80mm auto' : 
                   settings.paperSize === 'thermal_58mm' ? '58mm auto' : 'A4'};
          }
          
          .no-print {
            display: none !important;
          }
        }
      `}</style>
    </>
  )
}

export default InvoicePrint

