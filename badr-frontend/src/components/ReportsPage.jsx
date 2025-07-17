import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign, Package, Calendar } from 'lucide-react'

const ReportsPage = () => {
  const [salesReport, setSalesReport] = useState({ total_revenue: 0, total_sales: 0, sales: [] })
  const [expensesReport, setExpensesReport] = useState({ total_expenses: 0, expenses: [] })
  const [lowStockProducts, setLowStockProducts] = useState([])
  const [expiringWarranties, setExpiringWarranties] = useState([])
  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  })

  const fetchReports = async () => {
    try {
      // Fetch sales report
      const salesResponse = await fetch(`/api/sales/report?start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`)
      const salesData = await salesResponse.json()
      setSalesReport(salesData)

      // Fetch expenses report
      const expensesResponse = await fetch(`/api/expenses/report?start_date=${dateRange.start_date}&end_date=${dateRange.end_date}`)
      const expensesData = await expensesResponse.json()
      setExpensesReport(expensesData)

      // Fetch low stock products
      const lowStockResponse = await fetch('/api/products/low-stock?threshold=10')
      const lowStockData = await lowStockResponse.json()
      setLowStockProducts(lowStockData)

      // Fetch expiring warranties
      const warrantiesResponse = await fetch('/api/warranties/expiring?days=30')
      const warrantiesData = await warrantiesResponse.json()
      setExpiringWarranties(warrantiesData)
    } catch (error) {
      console.error('Error fetching reports:', error)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [dateRange])

  const netProfit = salesReport.total_revenue - expensesReport.total_expenses

  const chartData = [
    { name: 'الإيرادات', value: salesReport.total_revenue, color: '#10b981' },
    { name: 'المصروفات', value: expensesReport.total_expenses, color: '#ef4444' },
    { name: 'صافي الربح', value: netProfit, color: netProfit >= 0 ? '#3b82f6' : '#f59e0b' }
  ]

  const pieData = [
    { name: 'الإيرادات', value: salesReport.total_revenue, color: '#10b981' },
    { name: 'المصروفات', value: expensesReport.total_expenses, color: '#ef4444' }
  ]

  return (
    <div className="space-y-6">
      {/* Date Range Filter */}
      <Card>
        <CardHeader>
          <CardTitle>فترة التقرير</CardTitle>
          <CardDescription>اختر الفترة الزمنية للتقرير</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <Label htmlFor="start_date">من تاريخ</Label>
              <Input
                id="start_date"
                type="date"
                value={dateRange.start_date}
                onChange={(e) => setDateRange({ ...dateRange, start_date: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="end_date">إلى تاريخ</Label>
              <Input
                id="end_date"
                type="date"
                value={dateRange.end_date}
                onChange={(e) => setDateRange({ ...dateRange, end_date: e.target.value })}
              />
            </div>
            <Button onClick={fetchReports}>
              <Calendar className="mr-2 h-4 w-4" />
              تحديث التقرير
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Financial Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">إجمالي الإيرادات</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {salesReport.total_revenue.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              من {salesReport.total_sales} مبيعة
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">إجمالي المصروفات</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {expensesReport.total_expenses.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              من {expensesReport.expenses.length} مصروف
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">صافي الربح</CardTitle>
            <DollarSign className={`h-4 w-4 ${netProfit >= 0 ? 'text-blue-600' : 'text-orange-600'}`} />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${netProfit >= 0 ? 'text-blue-600' : 'text-orange-600'}`}>
              {netProfit.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {netProfit >= 0 ? 'ربح' : 'خسارة'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>مقارنة الإيرادات والمصروفات</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>توزيع الإيرادات والمصروفات</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Low Stock Alert */}
        {lowStockProducts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-red-600" />
                تنبيه: منتجات قليلة المخزون
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>تحذير!</AlertTitle>
                <AlertDescription>
                  يوجد {lowStockProducts.length} منتج بكمية قليلة في المخزون
                </AlertDescription>
              </Alert>
              <Table className="mt-4">
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-right">المنتج</TableHead>
                    <TableHead className="text-right">الكمية المتبقية</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {lowStockProducts.slice(0, 5).map((product) => (
                    <TableRow key={product.id}>
                      <TableCell>{product.name}</TableCell>
                      <TableCell className="text-red-600 font-bold">{product.quantity}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {/* Expiring Warranties Alert */}
        {expiringWarranties.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                تنبيه: ضمانات منتهية الصلاحية
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>تحذير!</AlertTitle>
                <AlertDescription>
                  يوجد {expiringWarranties.length} ضمان سينتهي خلال 30 يوم
                </AlertDescription>
              </Alert>
              <Table className="mt-4">
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-right">رقم الضمان</TableHead>
                    <TableHead className="text-right">تاريخ الانتهاء</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {expiringWarranties.slice(0, 5).map((warranty) => (
                    <TableRow key={warranty.id}>
                      <TableCell>#{warranty.id}</TableCell>
                      <TableCell className="text-orange-600 font-bold">
                        {new Date(warranty.end_date).toLocaleDateString('ar-IQ')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

export default ReportsPage

