import { useState, useEffect } from 'react'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { 
  Settings, 
  Printer, 
  FileText, 
  Upload, 
  Save, 
  RotateCcw,
  Phone,
  MapPin,
  Mail,
  Globe,
  Building,
  User,
  Image as ImageIcon,
  Palette,
  Type,
  Layout
} from 'lucide-react'

const PrintSettings = () => {
  const [storeInfo, setStoreInfo] = useState({
    name: 'البدر للإنارة',
    description: 'محل متخصص في جميع أنواع الإنارة والكهربائيات',
    phone: '07XX XXX XXXX',
    email: '',
    address: 'بغداد - العراق',
    website: '',
    taxNumber: '',
    commercialRecord: '',
    logo: null
  })

  const [printDefaults, setPrintDefaults] = useState({
    paperSize: 'A4',
    fontSize: 'medium',
    template: 'standard',
    showLogo: true,
    showCustomerInfo: true,
    showItemDetails: true,
    showWarranty: true,
    showNotes: true,
    includeQR: false,
    includeBarcode: false,
    colorScheme: 'blue',
    headerStyle: 'modern',
    footerText: 'شكراً لتعاملكم معنا'
  })

  const [thermalSettings, setThermalSettings] = useState({
    printerWidth: '80mm',
    cutPaper: true,
    openDrawer: false,
    copies: 1,
    encoding: 'utf8'
  })

  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      // Load settings from localStorage or API
      const savedStoreInfo = localStorage.getItem('storeInfo')
      const savedPrintDefaults = localStorage.getItem('printDefaults')
      const savedThermalSettings = localStorage.getItem('thermalSettings')

      if (savedStoreInfo) {
        setStoreInfo(JSON.parse(savedStoreInfo))
      }
      if (savedPrintDefaults) {
        setPrintDefaults(JSON.parse(savedPrintDefaults))
      }
      if (savedThermalSettings) {
        setThermalSettings(JSON.parse(savedThermalSettings))
      }
    } catch (error) {
      console.error('Error loading settings:', error)
    }
  }

  const saveSettings = async () => {
    setIsSaving(true)
    try {
      // Save to localStorage (in a real app, this would be saved to the backend)
      localStorage.setItem('storeInfo', JSON.stringify(storeInfo))
      localStorage.setItem('printDefaults', JSON.stringify(printDefaults))
      localStorage.setItem('thermalSettings', JSON.stringify(thermalSettings))
      
      alert('تم حفظ الإعدادات بنجاح')
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('حدث خطأ في حفظ الإعدادات')
    } finally {
      setIsSaving(false)
    }
  }

  const resetToDefaults = () => {
    if (confirm('هل أنت متأكد من إعادة تعيين جميع الإعدادات إلى القيم الافتراضية؟')) {
      setStoreInfo({
        name: 'البدر للإنارة',
        description: 'محل متخصص في جميع أنواع الإنارة والكهربائيات',
        phone: '07XX XXX XXXX',
        email: '',
        address: 'بغداد - العراق',
        website: '',
        taxNumber: '',
        commercialRecord: '',
        logo: null
      })

      setPrintDefaults({
        paperSize: 'A4',
        fontSize: 'medium',
        template: 'standard',
        showLogo: true,
        showCustomerInfo: true,
        showItemDetails: true,
        showWarranty: true,
        showNotes: true,
        includeQR: false,
        includeBarcode: false,
        colorScheme: 'blue',
        headerStyle: 'modern',
        footerText: 'شكراً لتعاملكم معنا'
      })

      setThermalSettings({
        printerWidth: '80mm',
        cutPaper: true,
        openDrawer: false,
        copies: 1,
        encoding: 'utf8'
      })
    }
  }

  const handleLogoUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setStoreInfo({...storeInfo, logo: e.target.result})
      }
      reader.readAsDataURL(file)
    }
  }

  const testPrint = () => {
    // Create a test invoice for preview
    const testInvoice = {
      id: 'TEST-001',
      date: new Date().toISOString(),
      customer: { name: 'زبون تجريبي', phone: '07XX XXX XXXX' },
      items: [
        { name: 'لمبة LED 12 واط', quantity: 2, price: 15000 },
        { name: 'مفتاح كهربائي', quantity: 1, price: 8000 }
      ],
      total: 38000,
      currency: 'IQD'
    }

    // This would open the print preview with test data
    alert('سيتم فتح معاينة الطباعة مع بيانات تجريبية')
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Settings className="w-8 h-8 text-blue-600" />
            إعدادات الطباعة
          </h1>
          <p className="text-gray-600 mt-1">تخصيص إعدادات الفواتير والطباعة</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={testPrint}>
            <Printer className="w-4 h-4 mr-2" />
            اختبار الطباعة
          </Button>
          <Button variant="outline" onClick={resetToDefaults}>
            <RotateCcw className="w-4 h-4 mr-2" />
            إعادة تعيين
          </Button>
          <Button onClick={saveSettings} disabled={isSaving}>
            <Save className="w-4 h-4 mr-2" />
            {isSaving ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Store Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building className="w-5 h-5 text-blue-600" />
              معلومات المحل
            </CardTitle>
            <CardDescription>
              المعلومات التي ستظهر في رأس الفواتير
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">اسم المحل</label>
              <input
                type="text"
                value={storeInfo.name}
                onChange={(e) => setStoreInfo({...storeInfo, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">وصف المحل</label>
              <textarea
                value={storeInfo.description}
                onChange={(e) => setStoreInfo({...storeInfo, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="2"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">رقم الهاتف</label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    value={storeInfo.phone}
                    onChange={(e) => setStoreInfo({...storeInfo, phone: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">البريد الإلكتروني</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="email"
                    value={storeInfo.email}
                    onChange={(e) => setStoreInfo({...storeInfo, email: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">العنوان</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  value={storeInfo.address}
                  onChange={(e) => setStoreInfo({...storeInfo, address: e.target.value})}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">الموقع الإلكتروني</label>
                <div className="relative">
                  <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    value={storeInfo.website}
                    onChange={(e) => setStoreInfo({...storeInfo, website: e.target.value})}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">الرقم الضريبي</label>
                <input
                  type="text"
                  value={storeInfo.taxNumber}
                  onChange={(e) => setStoreInfo({...storeInfo, taxNumber: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">شعار المحل</label>
              <div className="flex items-center gap-4">
                {storeInfo.logo ? (
                  <img
                    src={storeInfo.logo}
                    alt="شعار المحل"
                    className="w-16 h-16 object-cover rounded-lg border"
                  />
                ) : (
                  <div className="w-16 h-16 bg-gray-200 rounded-lg flex items-center justify-center">
                    <ImageIcon className="w-8 h-8 text-gray-400" />
                  </div>
                )}
                <div>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleLogoUpload}
                    className="hidden"
                    id="logo-upload"
                  />
                  <label
                    htmlFor="logo-upload"
                    className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    <Upload className="w-4 h-4" />
                    رفع شعار
                  </label>
                  <p className="text-xs text-gray-600 mt-1">PNG, JPG حتى 2MB</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Print Defaults */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-600" />
              إعدادات الطباعة الافتراضية
            </CardTitle>
            <CardDescription>
              الإعدادات الافتراضية لطباعة الفواتير
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">حجم الورق</label>
                <select
                  value={printDefaults.paperSize}
                  onChange={(e) => setPrintDefaults({...printDefaults, paperSize: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="A4">A4 (210mm)</option>
                  <option value="thermal_80mm">حراري 80mm</option>
                  <option value="thermal_58mm">حراري 58mm</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">حجم الخط</label>
                <select
                  value={printDefaults.fontSize}
                  onChange={(e) => setPrintDefaults({...printDefaults, fontSize: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="small">صغير</option>
                  <option value="medium">متوسط</option>
                  <option value="large">كبير</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">قالب الطباعة</label>
                <select
                  value={printDefaults.template}
                  onChange={(e) => setPrintDefaults({...printDefaults, template: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="standard">قياسي</option>
                  <option value="thermal">حراري</option>
                  <option value="minimal">مبسط</option>
                  <option value="detailed">مفصل</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">نظام الألوان</label>
                <select
                  value={printDefaults.colorScheme}
                  onChange={(e) => setPrintDefaults({...printDefaults, colorScheme: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="blue">أزرق</option>
                  <option value="green">أخضر</option>
                  <option value="purple">بنفسجي</option>
                  <option value="gray">رمادي</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">نص التذييل</label>
              <input
                type="text"
                value={printDefaults.footerText}
                onChange={(e) => setPrintDefaults({...printDefaults, footerText: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="space-y-3">
              <h4 className="font-medium">العناصر المعروضة</h4>
              <div className="grid grid-cols-2 gap-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.showLogo}
                    onChange={(e) => setPrintDefaults({...printDefaults, showLogo: e.target.checked})}
                  />
                  <span className="text-sm">الشعار</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.showCustomerInfo}
                    onChange={(e) => setPrintDefaults({...printDefaults, showCustomerInfo: e.target.checked})}
                  />
                  <span className="text-sm">معلومات الزبون</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.showItemDetails}
                    onChange={(e) => setPrintDefaults({...printDefaults, showItemDetails: e.target.checked})}
                  />
                  <span className="text-sm">تفاصيل المنتجات</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.showWarranty}
                    onChange={(e) => setPrintDefaults({...printDefaults, showWarranty: e.target.checked})}
                  />
                  <span className="text-sm">معلومات الضمان</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.includeQR}
                    onChange={(e) => setPrintDefaults({...printDefaults, includeQR: e.target.checked})}
                  />
                  <span className="text-sm">رمز QR</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={printDefaults.includeBarcode}
                    onChange={(e) => setPrintDefaults({...printDefaults, includeBarcode: e.target.checked})}
                  />
                  <span className="text-sm">الباركود</span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Thermal Printer Settings */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Printer className="w-5 h-5 text-purple-600" />
              إعدادات الطابعة الحرارية
            </CardTitle>
            <CardDescription>
              إعدادات خاصة بطابعات الفواتير الحرارية
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">عرض الطابعة</label>
                <select
                  value={thermalSettings.printerWidth}
                  onChange={(e) => setThermalSettings({...thermalSettings, printerWidth: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="58mm">58mm</option>
                  <option value="80mm">80mm</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">عدد النسخ</label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={thermalSettings.copies}
                  onChange={(e) => setThermalSettings({...thermalSettings, copies: parseInt(e.target.value)})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">ترميز النص</label>
                <select
                  value={thermalSettings.encoding}
                  onChange={(e) => setThermalSettings({...thermalSettings, encoding: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="utf8">UTF-8</option>
                  <option value="cp1256">CP1256</option>
                  <option value="iso8859-6">ISO 8859-6</option>
                </select>
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={thermalSettings.cutPaper}
                    onChange={(e) => setThermalSettings({...thermalSettings, cutPaper: e.target.checked})}
                  />
                  <span className="text-sm">قطع الورق تلقائياً</span>
                </label>

                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={thermalSettings.openDrawer}
                    onChange={(e) => setThermalSettings({...thermalSettings, openDrawer: e.target.checked})}
                  />
                  <span className="text-sm">فتح درج النقد</span>
                </label>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default PrintSettings

