import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Shield, 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Plus,
  Search,
  Filter,
  Calendar,
  User,
  Package,
  FileText,
  Bell,
  Settings,
  Eye,
  Edit,
  Trash2
} from 'lucide-react';

const WarrantyPage = () => {
  const [warranties, setWarranties] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [expiringFilter, setExpiringFilter] = useState('all');
  const [showAddModal, setShowAddModal] = useState(false);
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [selectedWarranty, setSelectedWarranty] = useState(null);
  const [claimDetails, setClaimDetails] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [warrantiesRes, templatesRes, statsRes] = await Promise.all([
        fetch('http://localhost:5001/api/warranties'),
        fetch('http://localhost:5001/api/warranty-templates'),
        fetch('http://localhost:5001/api/warranties/stats')
      ]);

      const [warrantiesData, templatesData, statsData] = await Promise.all([
        warrantiesRes.json(),
        templatesRes.json(),
        statsRes.json()
      ]);

      setWarranties(warrantiesData);
      setTemplates(templatesData);
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaimWarranty = async () => {
    if (!selectedWarranty || !claimDetails.trim()) {
      alert('يرجى إدخال تفاصيل المطالبة');
      return;
    }

    try {
      const response = await fetch(`http://localhost:5001/api/warranties/${selectedWarranty.id}/claim`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          claim_details: claimDetails
        }),
      });

      if (response.ok) {
        alert('تم تسجيل مطالبة الضمان بنجاح');
        setShowClaimModal(false);
        setSelectedWarranty(null);
        setClaimDetails('');
        fetchData();
      } else {
        alert('حدث خطأ في تسجيل المطالبة');
      }
    } catch (error) {
      console.error('Error claiming warranty:', error);
      alert('حدث خطأ في الاتصال');
    }
  };

  const checkNotifications = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/warranties/check-notifications', {
        method: 'POST',
      });

      const result = await response.json();
      alert(result.message);
      fetchData();
    } catch (error) {
      console.error('Error checking notifications:', error);
      alert('حدث خطأ في فحص الإشعارات');
    }
  };

  const getStatusColor = (warranty) => {
    const status = warranty.warranty_status;
    switch (status.color) {
      case 'green': return 'bg-green-100 text-green-800';
      case 'yellow': return 'bg-yellow-100 text-yellow-800';
      case 'red': return 'bg-red-100 text-red-800';
      case 'blue': return 'bg-blue-100 text-blue-800';
      case 'gray': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (warranty) => {
    const status = warranty.warranty_status.status;
    switch (status) {
      case 'active': return <ShieldCheck className="w-4 h-4" />;
      case 'expiring_month':
      case 'expiring_soon': return <ShieldAlert className="w-4 h-4" />;
      case 'expired': return <ShieldX className="w-4 h-4" />;
      case 'claimed': return <CheckCircle className="w-4 h-4" />;
      case 'void': return <XCircle className="w-4 h-4" />;
      default: return <Shield className="w-4 h-4" />;
    }
  };

  const filteredWarranties = warranties.filter(warranty => {
    const matchesSearch = warranty.product_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         warranty.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         warranty.customer_phone?.includes(searchTerm);
    
    const matchesStatus = statusFilter === 'all' || warranty.status === statusFilter;
    
    let matchesExpiring = true;
    if (expiringFilter === 'expiring_30') {
      matchesExpiring = warranty.days_remaining <= 30 && warranty.days_remaining > 0;
    } else if (expiringFilter === 'expiring_7') {
      matchesExpiring = warranty.days_remaining <= 7 && warranty.days_remaining > 0;
    } else if (expiringFilter === 'expired') {
      matchesExpiring = warranty.days_remaining === 0;
    }
    
    return matchesSearch && matchesStatus && matchesExpiring;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Shield className="w-8 h-8 text-blue-600" />
            إدارة الضمانات
          </h1>
          <p className="text-gray-600 mt-1">نظام ذكي لإدارة ومتابعة ضمانات المنتجات</p>
        </div>
        <div className="flex gap-3">
          <Button onClick={checkNotifications} className="flex items-center gap-2">
            <Bell className="w-4 h-4" />
            فحص الإشعارات
          </Button>
          <Button onClick={() => setShowAddModal(true)} className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            ضمان جديد
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100">إجمالي الضمانات</p>
                <p className="text-3xl font-bold">{stats.total_warranties || 0}</p>
              </div>
              <Shield className="w-12 h-12 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100">ضمانات سارية</p>
                <p className="text-3xl font-bold">{stats.active_warranties || 0}</p>
              </div>
              <ShieldCheck className="w-12 h-12 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100">تنتهي خلال 30 يوم</p>
                <p className="text-3xl font-bold">{stats.expiring_30_days || 0}</p>
              </div>
              <ShieldAlert className="w-12 h-12 text-yellow-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-red-500 to-red-600 text-white">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100">منتهية الصلاحية</p>
                <p className="text-3xl font-bold">{stats.expired || 0}</p>
              </div>
              <ShieldX className="w-12 h-12 text-red-200" />
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
                  placeholder="البحث بالمنتج، العميل، أو الهاتف..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">جميع الحالات</option>
              <option value="active">سارية</option>
              <option value="claimed">مطالب بها</option>
              <option value="expired">منتهية</option>
              <option value="void">ملغية</option>
            </select>

            <select
              value={expiringFilter}
              onChange={(e) => setExpiringFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">جميع الفترات</option>
              <option value="expiring_30">تنتهي خلال 30 يوم</option>
              <option value="expiring_7">تنتهي خلال 7 أيام</option>
              <option value="expired">منتهية</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Warranties List */}
      <Card>
        <CardHeader>
          <CardTitle>قائمة الضمانات</CardTitle>
          <CardDescription>
            عرض {filteredWarranties.length} من أصل {warranties.length} ضمان
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredWarranties.length === 0 ? (
            <div className="text-center py-12">
              <Shield className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد ضمانات</h3>
              <p className="text-gray-600">لم يتم العثور على ضمانات تطابق المعايير المحددة.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-right py-3 px-4 font-medium text-gray-700">المنتج</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">العميل</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">نوع الضمان</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">تاريخ الانتهاء</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">الحالة</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">الأيام المتبقية</th>
                    <th className="text-right py-3 px-4 font-medium text-gray-700">الإجراءات</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredWarranties.map((warranty) => (
                    <tr key={warranty.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <Package className="w-5 h-5 text-gray-400" />
                          <span className="font-medium">{warranty.product_name || 'غير محدد'}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{warranty.customer_name || 'غير محدد'}</div>
                          <div className="text-sm text-gray-600">{warranty.customer_phone || ''}</div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">{warranty.warranty_type}</Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <span>{warranty.end_date}</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={getStatusColor(warranty)}>
                          <div className="flex items-center gap-1">
                            {getStatusIcon(warranty)}
                            {warranty.warranty_status.message}
                          </div>
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className={warranty.days_remaining <= 7 ? 'text-red-600 font-bold' : 
                                         warranty.days_remaining <= 30 ? 'text-yellow-600 font-medium' : 
                                         'text-green-600'}>
                            {warranty.days_remaining} يوم
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedWarranty(warranty);
                              setShowClaimModal(true);
                            }}
                            disabled={warranty.status !== 'active'}
                          >
                            <FileText className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Eye className="w-4 h-4" />
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

      {/* Claim Modal */}
      {showClaimModal && selectedWarranty && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>مطالبة ضمان</CardTitle>
              <CardDescription>
                تسجيل مطالبة ضمان للمنتج: {selectedWarranty.product_name}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">تفاصيل المطالبة</label>
                <textarea
                  value={claimDetails}
                  onChange={(e) => setClaimDetails(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="اكتب تفاصيل المشكلة أو سبب المطالبة..."
                  rows="4"
                />
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowClaimModal(false);
                    setSelectedWarranty(null);
                    setClaimDetails('');
                  }}
                  className="flex-1"
                >
                  إلغاء
                </Button>
                <Button
                  onClick={handleClaimWarranty}
                  className="flex-1"
                >
                  تسجيل المطالبة
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default WarrantyPage;

