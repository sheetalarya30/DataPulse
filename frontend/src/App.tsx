import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Navbar } from "./components/Navbar";
import { TriggerRunModal } from "./components/TriggerRunModal";
import { OverviewPage } from "./pages/OverviewPage";
import { PipelinesPage } from "./pages/PipelinesPage";
import { PipelineDetailPage } from "./pages/PipelineDetailPage";
import { IncidentsPage } from "./pages/IncidentsPage";
import { DataQualityPage } from "./pages/DataQualityPage";
import { RecoveryCenterPage } from "./pages/RecoveryCenterPage";

export const App: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [triggerModalOpen, setTriggerModalOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-navy-950 text-slate-100 flex">
        {/* Collapsible Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Global Trigger Run Modal */}
        <TriggerRunModal
          isOpen={triggerModalOpen}
          onClose={() => setTriggerModalOpen(false)}
          onSuccess={() => {
            // Reload window or trigger dispatch
            window.location.reload();
          }}
        />

        {/* Main Content Area */}
        <div
          className={`flex-1 flex flex-col transition-all duration-300 ${
            sidebarCollapsed ? "ml-20" : "ml-64"
          }`}
        >
          <Navbar onOpenTriggerModal={() => setTriggerModalOpen(true)} />

          <main className="flex-1 pb-12">
            <Routes>
              <Route
                path="/"
                element={<OverviewPage onOpenTriggerModal={() => setTriggerModalOpen(true)} />}
              />
              <Route
                path="/pipelines"
                element={<PipelinesPage onOpenTriggerModal={() => setTriggerModalOpen(true)} />}
              />
              <Route
                path="/pipelines/:id"
                element={<PipelineDetailPage onOpenTriggerModal={() => setTriggerModalOpen(true)} />}
              />
              <Route path="/incidents" element={<IncidentsPage />} />
              <Route path="/quality" element={<DataQualityPage />} />
              <Route path="/recovery" element={<RecoveryCenterPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
};

export default App;
