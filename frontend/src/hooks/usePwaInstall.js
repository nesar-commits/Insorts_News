import { useEffect, useState } from 'react'

function isIos() {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent)
}

function isStandalone() {
  return window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true
}

export function usePwaInstall() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [installed, setInstalled] = useState(isStandalone)

  useEffect(() => {
    const handleBeforeInstallPrompt = (event) => {
      // Suppress Chrome's own mini-infobar so our button is the one place
      // users are told to install from — otherwise both show up and it's
      // inconsistent across visits.
      event.preventDefault()
      setDeferredPrompt(event)
    }
    const handleAppInstalled = () => {
      setInstalled(true)
      setDeferredPrompt(null)
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleAppInstalled)
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
      window.removeEventListener('appinstalled', handleAppInstalled)
    }
  }, [])

  const install = async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    if (outcome === 'accepted') setInstalled(true)
    setDeferredPrompt(null)
  }

  return {
    // Chrome/Edge/Android: a real native prompt we can trigger directly.
    canInstall: !installed && !!deferredPrompt,
    // iOS Safari never fires beforeinstallprompt — show manual steps instead.
    needsIosInstructions: !installed && isIos() && !deferredPrompt,
    installed,
    install,
  }
}
