import { Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { ScrollManager } from './components/ScrollManager'
import { Feed } from './pages/Feed'
import { SearchPage } from './pages/SearchPage'
import { ArticleDetail } from './pages/ArticleDetail'
import { Bookmarks } from './pages/Bookmarks'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Profile } from './pages/Profile'
import { Briefs } from './pages/Briefs'
import { NotFound } from './pages/NotFound'

function App() {
  return (
    <>
      <ScrollManager />
      <Routes>
        {/* Briefs renders full-bleed, edge-to-edge — deliberately outside the padded Layout shell */}
        <Route path="/briefs" element={<Briefs />} />

        <Route element={<Layout />}>
          <Route path="/" element={<Feed />} />
          <Route path="/category/:slug" element={<Feed />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/bookmarks"
            element={
              <ProtectedRoute>
                <Bookmarks />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
