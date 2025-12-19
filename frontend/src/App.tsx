/**
 * Main application component
 */

import React, { useState } from 'react';
import { FileUploader } from './components/upload/FileUploader';
import { Dashboard } from './components/dashboard/Dashboard';
import { uploadFile, analyzeFile, exportAnalysis, downloadExport } from './services/api';
import type { AnalysisResult, ExportRequest } from './types';
import { Download, FileSpreadsheet, CheckCircle } from 'lucide-react';

type AppState = 'upload' | 'analyzing' | 'results';

function App() {
  const [state, setState] = useState<AppState>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadId, setUploadId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file);
    setError(null);
    setIsProcessing(true);
    setState('analyzing');

    try {
      // Step 1: Upload file
      const uploadResponse = await uploadFile(file);
      setUploadId(uploadResponse.upload_id);

      // Step 2: Analyze file
      const analysisResult = await analyzeFile(uploadResponse.upload_id);
      setAnalysis(analysisResult);
      setState('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error procesando archivo');
      setState('upload');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async (format: 'excel' | 'json') => {
    if (!analysis) return;

    try {
      const request: ExportRequest = { format };
      const exportResponse = await exportAnalysis(analysis.analysis_id, request);

      // Trigger download
      const downloadUrl = downloadExport(exportResponse.export_id);
      window.open(downloadUrl, '_blank');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error exportando resultados');
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setUploadId(null);
    setAnalysis(null);
    setError(null);
    setState('upload');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileSpreadsheet className="w-8 h-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">
                Contraídos Visual Analyzer
              </h1>
            </div>
            {analysis && (
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Nuevo Análisis
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload State */}
        {state === 'upload' && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                Analiza tus archivos de contraídos
              </h2>
              <p className="mt-2 text-lg text-gray-600">
                Sube un archivo Excel para obtener análisis detallado y validación automática
              </p>
            </div>
            <FileUploader onFileSelect={handleFileSelect} isUploading={isProcessing} />
            {error && (
              <div className="max-w-2xl mx-auto p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            )}
          </div>
        )}

        {/* Analyzing State */}
        {state === 'analyzing' && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">
              Analizando archivo...
            </h2>
            <p className="text-gray-600">{selectedFile?.name}</p>
            <div className="mt-8 space-y-2 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Validando estructura del archivo</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span>Aplicando reglas de negocio</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-gray-300 rounded-full animate-pulse" />
                <span>Generando análisis...</span>
              </div>
            </div>
          </div>
        )}

        {/* Results State */}
        {state === 'results' && analysis && (
          <div className="space-y-6">
            {/* Results Header */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">
                    Resultados del Análisis
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Archivo: {selectedFile?.name}
                  </p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => handleExport('excel')}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Exportar Excel
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Exportar JSON
                  </button>
                </div>
              </div>
            </div>

            {/* Dashboard */}
            <Dashboard analysis={analysis} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            Contraídos Visual Analyzer v1.0.0 - Herramienta de análisis contable
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
