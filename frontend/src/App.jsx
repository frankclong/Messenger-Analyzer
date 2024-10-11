import { react, useEffect} from 'react'
import {BrowserRouter, Routes, Route, Navigate, useNavigate} from 'react-router-dom'
import Login from "./pages/Login" 
import Home from "./pages/Home" 
import Register from "./pages/Register" 
import NotFound from "./pages/NotFound" 
import Upload from './pages/Upload'
import Analyze from './pages/Analyze'
import ProtectedRoute from "./components/ProtectedRoute"
import api from './api'

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" />
}

function RegisterAndLogout() {
  localStorage.clear()
  return <Register />
}



function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />}/>
        <Route path="/logout" element={<Logout />}/>
        <Route path="/register" element={<RegisterAndLogout />}/>
        <Route path="/upload" element={<Upload />}/>
        <Route path="/analyze" element={<Analyze />}/>
        <Route path="*" element={<NotFound />}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
