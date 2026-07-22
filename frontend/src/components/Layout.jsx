import { Outlet } from 'react-router-dom'
import { NavBar } from './NavBar'
import { BottomNav } from './BottomNav'

export function Layout() {
  return (
    <div className="flex min-h-full flex-col bg-gray-50 dark:bg-gray-950">
      <NavBar />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 pb-24 pt-5 sm:pb-10">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}
