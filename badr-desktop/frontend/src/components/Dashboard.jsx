import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { 
  DollarSign, 
  Package, 
  Users, 
  CreditCard, 
  TrendingUp, 
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalRevenue: 0,
    totalSales: 0,
    totalCustomers: 0,
    totalProducts: 0,
    lowStockItems: 0,
    expiredWarranties: 0,
    todayRevenue: 0,
    monthlyGrowth: 0
  })

  const [salesData, setSalesData] = useState([])
  const [productCategories, setProductCategories] = useState([])
  const [recentActivities, setRecentActivities] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Fetch dashboard statistics
      const response = await fetch('http://localhost:5001/api/dashboard/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }

      // Fetch sales chart data
      const salesResponse = await fetch('http://localhost:5001/api/dashboard/sales-chart')
      if (salesResponse.ok) {
        const salesData = await salesResponse.json()
        setSalesData(salesData)
      }

      // Fetch product categories data
      const categoriesResponse = await fetch('http://localhost:5001/api/dashboard/product-categories')
      if (categoriesResponse.ok) {
        const categoriesData = await categoriesResponse.json()
        setProductCategories(categoriesData)
      }

      // Fetch recent activities
      const activitiesResponse = await fetch('http://localhost:5001/api/dashboard/recent-activities')
      if (activitiesResponse.ok) {
        const activitiesData = await activitiesResponse.json()
        setRecentActivities(activitiesData)
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      // Set mock data for demonstration
      setStats({
        totalRevenue: 45231.89,
        totalSales: 2350,
        totalCustomers: 150,
        totalProducts: 573,
        lowStockItems: 12,
        expiredWarranties: 3,
        todayRevenue: 1250.50,
        monthlyGrowth: 20.1
      })

      setSalesData([
        { name: 'يناير', sales: 4000, revenue: 2400 },
        { name: 'فبراير', sales: 3000, revenue: 1398 },
        { name: 'مارس', sales: 2000, revenue: 9800 },
        { name: 'أبريل', sales: 2780, revenue: 3908 },
        { name: 'مايو', sales: 1890, revenue: 4800 },
        { name: 'يونيو', sales: 2390, revenue: 3800 },
        { name: 'يوليو', sales: 3490, revenue: 4300 }
      ])

      setProductCategories([
        { name: 'إضاءة LED', value: 400, color: '#0088FE' },
        { name: 'مصابيح كلاسيكية', value: 300, color: '#00C49F' },
        { name: 'إكسسوارات', value: 200, color: '#FFBB28' },
        { name: 'أدوات كهربائية', value: 100, color: '#FF8042' }
      ])

      setRecentActivities([
        { id: 1, type: 'sale', description: 'بيع مصباح LED للزبون أحمد محمد', time: '10 دقائق', amount: 150 },
        { id: 2, type: 'stock', description: 'إضافة 50 قطعة من مصابيح الفلورسنت', time: '30 دقيقة', amount: null },
        { id: 3, type: 'customer', description: 'تسجيل زبون جديد: فاطمة علي', time: '1 ساعة', amount: null },
        { id: 4, type: 'warranty', description: 'انتهاء ضمان مصباح للزبون محمد حسن', time: '2 ساعة', amount: null }
      ])
    }
  }

  const StatCard = ({ title, value, change, icon: Icon, trend, color = "blue" }) => {
    const colorClasses = {
      blue: "from-blue-500 to-blue-600",
      green: "from-green-500 to-green-600", 
      purple: "from-purple-500 to-purple-600",
      orange: "from-orange-500 to-orange-600",
      red: "from-red-500 to-red-600",
      yellow: "from-yellow-500 to-yellow-600"
    }

    return (
      <Card className="relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:scale-105">
        <div className={`absolute inset-0 bg-gradient-to-r ${colorClasses[color]} opacity-10`}></div>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-700">{title}</CardTitle>
          <div className={`p-2 rounded-full bg-gradient-to-r ${colorClasses[color]}`}>
            <Icon className="h-4 w-4 text-white" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
          {change && (
            <div className="flex items-center text-xs mt-1">
              {trend === 'up' ? (
                <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 text-red-500 mr-1" />
              )}
              <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
                {change}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const ActivityIcon = ({ type }) => {
    switch (type) {
      case 'sale':
        return <CreditCard className="h-4 w-4 text-green-500" />
      case 'stock':
        return <Package className="h-4 w-4 text-blue-500" />
      case 'customer':
        return <Users className="h-4 w-4 text-purple-500" />
      case 'warranty':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <div className="space-y-6 p-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">مرحباً بك في البدر للإنارة</h1>
        <p className="text-blue-100">إليك نظرة سريعة على أداء محلك اليوم</p>
      </div>

      {/* Main Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="إجمالي الإيرادات"
          value={`$${stats.totalRevenue.toLocaleString()}`}
          change={`+${stats.monthlyGrowth}% من الشهر الماضي`}
          icon={DollarSign}
          trend="up"
          color="green"
        />
        <StatCard
          title="المبيعات"
          value={`+${stats.totalSales.toLocaleString()}`}
          change="+180.1% من الشهر الماضي"
          icon={CreditCard}
          trend="up"
          color="blue"
        />
        <StatCard
          title="الزبائن"
          value={`+${stats.totalCustomers}`}
          change="+19% من الشهر الماضي"
          icon={Users}
          trend="up"
          color="purple"
        />
        <StatCard
          title="المنتجات في المخزون"
          value={stats.totalProducts}
          change="-5% منذ آخر زيارة"
          icon={Package}
          trend="down"
          color="orange"
        />
      </div>

      {/* Secondary Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="إيرادات اليوم"
          value={`$${stats.todayRevenue.toLocaleString()}`}
          icon={DollarSign}
          color="green"
        />
        <StatCard
          title="منتجات قليلة المخزون"
          value={stats.lowStockItems}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="ضمانات منتهية"
          value={stats.expiredWarranties}
          icon={Clock}
          color="yellow"
        />
      </div>

      {/* Charts Section */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Sales Chart */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              مبيعات الأشهر السابقة
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="sales" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Product Categories Chart */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>توزيع المنتجات حسب الفئة</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={productCategories}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {productCategories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activities */}
      <Card>
        <CardHeader>
          <CardTitle>الأنشطة الأخيرة</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors">
                <ActivityIcon type={activity.type} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                  <p className="text-xs text-gray-500">منذ {activity.time}</p>
                </div>
                {activity.amount && (
                  <div className="text-sm font-semibold text-green-600">
                    ${activity.amount}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

