import { createContext, useContext } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

export const ToastContext = createContext(() => {})
export const useToast = () => useContext(ToastContext)

const colors = { info: 'bg-slate-800', success: 'bg-emerald-600', error: 'bg-rose-600' }

export function Toaster({ toasts }) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      <AnimatePresence>
        {toasts.map(t => (
          <motion.div key={t.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className={`${colors[t.type] || colors.info} text-white text-sm px-4 py-2 rounded-xl shadow-lg`}>
            {t.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
