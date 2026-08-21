import { useState } from 'react'
import { api } from '../lib/api'

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

export default function PaymentButton({ slotId, slotRent, userName, userEmail, onPaid }) {
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
    <div>
      <button
        onClick={handlePay} disabled={loading}
        className="px-6 py-3 rounded-lg bg-accentGold text-primary font-semibold disabled:opacity-50"
      >
        {loading ? 'Opening checkout…' : `Pay ₹${slotRent} & book this slot`}
      </button>
      {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
    </div>
  )
}
