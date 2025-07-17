import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Send, Settings, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

const TelegramSettings = () => {
  const [settings, setSettings] = useState({
    enabled: false,
    bot_token_configured: false,
    chat_id_configured: false
  });
  const [formData, setFormData] = useState({
    bot_token: '',
    chat_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/telegram/settings');
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:5001/api/telegram/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage('تم حفظ الإعدادات بنجاح!');
        setMessageType('success');
        fetchSettings();
        setFormData({ bot_token: '', chat_id: '' });
      } else {
        setMessage('فشل في حفظ الإعدادات');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('خطأ في الاتصال بالخادم');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleTestTelegram = async () => {
    setLoading(true);
    setMessage('');
    
    try {
      const response = await fetch('http://localhost:5001/api/telegram/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessage('تم إرسال رسالة الاختبار بنجاح!');
        setMessageType('success');
      } else {
        setMessage(data.message || 'فشل في إرسال رسالة الاختبار');
        setMessageType('error');
      }
    } catch (error) {
      setMessage('خطأ في الاتصال بالخادم');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = () => {
    if (settings.enabled) {
      return <Badge className="bg-green-100 text-green-800 border-green-200">
        <CheckCircle className="w-3 h-3 mr-1" />
        مفعل
      </Badge>;
    } else {
      return <Badge className="bg-red-100 text-red-800 border-red-200">
        <XCircle className="w-3 h-3 mr-1" />
        غير مفعل
      </Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* حالة التليجرام */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Send className="w-5 h-5 text-blue-600" />
                إعدادات التليجرام
              </CardTitle>
              <CardDescription>
                إعداد بوت التليجرام لإرسال الإشعارات الفورية
              </CardDescription>
            </div>
            {getStatusBadge()}
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${settings.bot_token_configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">Bot Token</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${settings.chat_id_configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm">Chat ID</span>
            </div>
          </div>

          {/* نموذج الإعدادات */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Bot Token</label>
              <input
                type="password"
                value={formData.bot_token}
                onChange={(e) => setFormData({...formData, bot_token: e.target.value})}
                placeholder="أدخل Bot Token هنا..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                احصل على Bot Token من @BotFather في التليجرام
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Chat ID</label>
              <input
                type="text"
                value={formData.chat_id}
                onChange={(e) => setFormData({...formData, chat_id: e.target.value})}
                placeholder="أدخل Chat ID هنا..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                احصل على Chat ID من @userinfobot في التليجرام
              </p>
            </div>

            <div className="flex gap-3">
              <Button 
                onClick={handleSaveSettings}
                disabled={loading || !formData.bot_token || !formData.chat_id}
                className="flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                {loading ? 'جاري الحفظ...' : 'حفظ الإعدادات'}
              </Button>

              {settings.enabled && (
                <Button 
                  onClick={handleTestTelegram}
                  disabled={loading}
                  variant="outline"
                  className="flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {loading ? 'جاري الإرسال...' : 'اختبار الإرسال'}
                </Button>
              )}
            </div>

            {message && (
              <div className={`p-3 rounded-md flex items-center gap-2 ${
                messageType === 'success' 
                  ? 'bg-green-100 text-green-800 border border-green-200' 
                  : 'bg-red-100 text-red-800 border border-red-200'
              }`}>
                {messageType === 'success' ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  <AlertCircle className="w-4 h-4" />
                )}
                {message}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* معلومات الإشعارات */}
      <Card>
        <CardHeader>
          <CardTitle>أنواع الإشعارات</CardTitle>
          <CardDescription>
            سيتم إرسال إشعارات فورية للعمليات التالية:
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                🛒
              </div>
              <div>
                <h4 className="font-medium">المبيعات</h4>
                <p className="text-sm text-gray-600">عند إتمام عملية بيع جديدة</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                📦
              </div>
              <div>
                <h4 className="font-medium">المنتجات</h4>
                <p className="text-sm text-gray-600">عند إضافة أو تعديل منتج</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
              <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
                💸
              </div>
              <div>
                <h4 className="font-medium">المصروفات</h4>
                <p className="text-sm text-gray-600">عند إضافة مصروف جديد</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                ⚠️
              </div>
              <div>
                <h4 className="font-medium">تنبيهات المخزون</h4>
                <p className="text-sm text-gray-600">عند نقص كمية المنتجات</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TelegramSettings;

