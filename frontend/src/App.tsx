import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { Login } from "./pages/Login";
import { Register } from "./pages/Register";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { CasesList } from "./pages/cases/CasesList";
import { CreateCase } from "./pages/cases/CreateCase";
import { CaseDetails } from "./pages/cases/CaseDetails";
import { ChatInterface } from "./pages/chat/ChatInterface";
import { RoadmapPage } from "./pages/roadmap/RoadmapPage";

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cases" element={<CasesList />} />
              <Route path="/cases/new" element={<CreateCase />} />
              <Route path="/cases/:id" element={<CaseDetails />} />
              <Route path="/cases/:id/edit" element={<CreateCase />} />
              <Route path="/cases/:id/roadmap" element={<RoadmapPage />} />
              
              <Route path="/chat" element={<ChatInterface />} />
              <Route path="/chat/:conversationId" element={<ChatInterface />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
