import { useState } from 'react'
import { api } from '../utils/api'

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) return resolve(true)
    const script = document.createElement('script')
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.onload = () => resolve(true)
    script.onerror = () => resolve(false)
    document.body.appendChild(script)
  })
}

/**
 * Razorpay checkout for booking one slot. The backend creates the order and
 * verifies the payment signature; on success the slot is marked occupied.
 */
export default function PaymentButton({ slotId, slotRent, userName, userEmail, onPaid, disabled, className = '' }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handlePay() {
    setLoading(true)
    setError('')
    try {
      const loaded = await loadRazorpayScript()
      if (!loaded) throw new Error('Could not load Razorpay checkout — check your connection')

      const order = await api.createOrder(slotId)

      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: 'CampusNest',
        description: 'Room booking payment',
        order_id: order.order_id,
        prefill: { name: userName, email: userEmail },
        theme: { color: '#f59e0b' },
        handler: async (response) => {
          try {
            const result = await api.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            })
            onPaid?.(result)
          } catch (e) {
            setError('Payment succeeded but verification failed — contact support with your payment ID.')
          }
        },
        modal: { ondismiss: () => setLoading(false) },
      })

      rzp.on('payment.failed', () => setError('Payment failed — please try again.'))
      rzp.open()
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={className}>
      <button onClick={handlePay} disabled={loading || disabled} className="btn-primary w-full">
        {loading ? 'Opening checkout…' : `Pay ₹${Number(slotRent).toLocaleString('en-IN')} & book`}
      </button>
      {error && <p className="text-rose-600 text-xs mt-1">{error}</p>}
    </div>
  )
}
