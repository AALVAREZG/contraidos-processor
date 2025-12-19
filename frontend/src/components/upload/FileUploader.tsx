/**
 * File upload component with drag & drop
 */

import React, { useState, useCallback } from 'react';
import { Upload, FileSpreadsheet, AlertCircle } from 'lucide-react';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  isUploading = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = (file: File): boolean => {
    const validExtensions = ['.xlsx', '.xls'];
    const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));

    if (!validExtensions.includes(fileExtension)) {
      setError(`Tipo de archivo inválido. Se permiten: ${validExtensions.join(', ')}`);
      return false;
    }

    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      setError('Archivo demasiado grande. Tamaño máximo: 50MB');
      return false;
    }

    setError(null);
    return true;
  };

  const handleFile = useCallback(
    (file: File) => {
      if (validateFile(file)) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-12
          transition-all duration-200
          ${isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-white'}
          ${isUploading ? 'opacity-50 pointer-events-none' : 'hover:border-primary-400'}
        `}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          accept=".xlsx,.xls"
          onChange={handleFileInput}
          disabled={isUploading}
        />

        <label htmlFor="file-input" className="cursor-pointer">
          <div className="flex flex-col items-center gap-4">
            {isUploading ? (
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600" />
            ) : (
              <div className="p-4 bg-primary-100 rounded-full">
                <Upload className="w-8 h-8 text-primary-600" />
              </div>
            )}

            <div className="text-center">
              <p className="text-lg font-semibold text-gray-700">
                {isUploading ? 'Subiendo archivo...' : 'Arrastra tu archivo aquí'}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                o haz clic para seleccionar
              </p>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <FileSpreadsheet className="w-4 h-4" />
              <span>Formatos: .xlsx, .xls (máx. 50MB)</span>
            </div>
          </div>
        </label>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Error</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};
