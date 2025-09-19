import { useEffect, useState } from 'react'

/**
 * Hook to check if component is mounted on client side
 * Prevents hydration mismatches from server/client differences
 */
export function useClientOnly() {
  const [isClient, setIsClient] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  return isClient
}

/**
 * Hook for safe localStorage access that prevents hydration issues
 */
export function useLocalStorage(key: string, initialValue: string = '') {
  const [storedValue, setStoredValue] = useState(initialValue)
  const isClient = useClientOnly()

  useEffect(() => {
    if (isClient) {
      try {
        const item = window.localStorage.getItem(key)
        if (item) {
          setStoredValue(item)
        }
      } catch (error) {
        console.warn(`Error reading localStorage key "${key}":`, error)
      }
    }
  }, [key, isClient])

  const setValue = (value: string) => {
    try {
      setStoredValue(value)
      if (isClient) {
        window.localStorage.setItem(key, value)
      }
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue] as const
}