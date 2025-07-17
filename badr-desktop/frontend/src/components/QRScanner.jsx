import { useEffect, useRef, useState } from 'react'
import { BrowserMultiFormatReader } from '@zxing/browser'
import { Button } from '@/components/ui/button.jsx'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog.jsx'
import { Camera, X } from 'lucide-react'

const QRScanner = ({ isOpen, onClose, onScan }) => {
  const videoRef = useRef(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState('')
  const codeReader = useRef(null)

  useEffect(() => {
    if (isOpen) {
      startScanning()
    } else {
      stopScanning()
    }

    return () => {
      stopScanning()
    }
  }, [isOpen])

  const startScanning = async () => {
    try {
      setError('')
      setIsScanning(true)
      
      if (!codeReader.current) {
        codeReader.current = new BrowserMultiFormatReader()
      }

      const videoInputDevices = await codeReader.current.listVideoInputDevices()
      
      if (videoInputDevices.length === 0) {
        setError('لم يتم العثور على كاميرا')
        return
      }

      // Use the first available camera (usually back camera on mobile)
      const selectedDeviceId = videoInputDevices[0].deviceId

      codeReader.current.decodeFromVideoDevice(
        selectedDeviceId,
        videoRef.current,
        (result, error) => {
          if (result) {
            onScan(result.getText())
            stopScanning()
            onClose()
          }
          if (error && error.name !== 'NotFoundException') {
            console.error('QR Scanner error:', error)
          }
        }
      )
    } catch (err) {
      console.error('Error starting QR scanner:', err)
      setError('خطأ في تشغيل الكاميرا: ' + err.message)
      setIsScanning(false)
    }
  }

  const stopScanning = () => {
    if (codeReader.current) {
      codeReader.current.reset()
    }
    setIsScanning(false)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]" dir="rtl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Camera className="h-5 w-5" />
            مسح رمز QR
          </DialogTitle>
          <DialogDescription>
            وجه الكاميرا نحو رمز QR للمنتج
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
          
          <div className="relative">
            <video
              ref={videoRef}
              className="w-full h-64 bg-black rounded-lg"
              autoPlay
              playsInline
              muted
            />
            
            {isScanning && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-48 h-48 border-2 border-blue-500 border-dashed rounded-lg animate-pulse"></div>
              </div>
            )}
          </div>
          
          {isScanning && (
            <div className="text-center text-sm text-gray-600">
              جاري البحث عن رمز QR...
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            <X className="mr-2 h-4 w-4" />
            إلغاء
          </Button>
          {!isScanning && (
            <Button onClick={startScanning}>
              <Camera className="mr-2 h-4 w-4" />
              بدء المسح
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default QRScanner

