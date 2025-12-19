/**
 * Detailed contraídos table with expandable rows
 */

import React, { useState } from 'react';
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle } from 'lucide-react';
import type { ContraidoGroup, Operation } from '../../types';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface DetailedContraidosTableProps {
  contraidos: ContraidoGroup[];
  orphanOperations: Operation[];
}

export const DetailedContraidosTable: React.FC<DetailedContraidosTableProps> = ({
  contraidos,
  orphanOperations,
}) => {
  const [expandedContraidos, setExpandedContraidos] = useState<Set<string>>(new Set());
  const [showOrphans, setShowOrphans] = useState(false);

  const toggleContraido = (numContraido: string) => {
    const newExpanded = new Set(expandedContraidos);
    if (newExpanded.has(numContraido)) {
      newExpanded.delete(numContraido);
    } else {
      newExpanded.add(numContraido);
    }
    setExpandedContraidos(newExpanded);
  };

  const renderOperationRow = (op: Operation) => (
    <tr key={op.num_operacion} className="bg-gray-50 border-b border-gray-200">
      <td className="px-4 py-3 text-sm text-gray-600">{op.num_operacion}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{op.ano}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{op.aplicacion}</td>
      <td className="px-4 py-3">
        <span
          className={`px-2 py-1 text-xs font-semibold rounded ${
            op.fase === 'AINP'
              ? 'bg-green-100 text-green-800'
              : 'bg-blue-100 text-blue-800'
          }`}
        >
          {op.fase}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-600 text-center">
        {op.estado || '-'}
      </td>
      <td className="px-4 py-3 text-sm font-medium text-right">
        {formatCurrency(op.importe)}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">{op.cpgc}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{formatDate(op.fecha)}</td>
      <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate" title={op.tercero}>
        {op.tercero}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600 max-w-md truncate" title={op.descripcion}>
        {op.descripcion}
      </td>
      <td className="px-4 py-3 text-center">
        {op.is_valid ? (
          <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-red-600 mx-auto" />
        )}
      </td>
    </tr>
  );

  return (
    <div className="space-y-6">
      {/* Main Contraídos Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Detalle por Contraído ({contraidos.length} contraídos)
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Haz clic en cada contraído para ver sus operaciones
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nº Contraído
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ops
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  AINP Total
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  M;P Válido
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  M;P Inválido
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Balance Neto
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {contraidos.map((contraido) => (
                <React.Fragment key={contraido.num_contraido}>
                  {/* Contraído Summary Row */}
                  <tr
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => toggleContraido(contraido.num_contraido)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <span className="font-medium text-gray-900">
                          {contraido.num_contraido}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {contraido.operations.length}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-700 font-medium">
                      {formatCurrency(contraido.total_arqueo)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-blue-700 font-medium">
                      {formatCurrency(contraido.total_cargo_valid)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-700 font-medium">
                      {formatCurrency(contraido.total_cargo_invalid)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-bold">
                      <span
                        className={
                          contraido.net_balance >= 0
                            ? 'text-green-700'
                            : 'text-red-700'
                        }
                      >
                        {formatCurrency(contraido.net_balance)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {contraido.has_invalid_operations ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-red-100 text-red-800">
                          Con Problemas
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded bg-green-100 text-green-800">
                          Válido
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {expandedContraidos.has(contraido.num_contraido) ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                    </td>
                  </tr>

                  {/* Expanded Operations */}
                  {expandedContraidos.has(contraido.num_contraido) && (
                    <tr>
                      <td colSpan={8} className="px-6 py-0">
                        <div className="py-4 bg-gray-50 border-t border-b border-gray-200">
                          <h4 className="text-sm font-semibold text-gray-700 mb-3 px-4">
                            Operaciones del Contraído {contraido.num_contraido}
                          </h4>
                          <div className="overflow-x-auto">
                            <table className="min-w-full">
                              <thead className="bg-gray-100">
                                <tr>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Nº Op
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Año
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Aplic
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Fase
                                  </th>
                                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-600">
                                    Estado
                                  </th>
                                  <th className="px-4 py-2 text-right text-xs font-medium text-gray-600">
                                    Importe
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    CPGC
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Fecha
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Tercero
                                  </th>
                                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-600">
                                    Descripción
                                  </th>
                                  <th className="px-4 py-2 text-center text-xs font-medium text-gray-600">
                                    Válido
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                {contraido.operations.map((op) =>
                                  renderOperationRow(op)
                                )}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Orphan Operations Table */}
      {orphanOperations.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div
            className="px-6 py-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 flex items-center justify-between"
            onClick={() => setShowOrphans(!showOrphans)}
          >
            <div>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-yellow-600" />
                Operaciones sin Contraído ({orphanOperations.length})
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Operaciones que no tienen número de contraído asignado
              </p>
            </div>
            {showOrphans ? (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-400" />
            )}
          </div>

          {showOrphans && (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Nº Op
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Año
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Aplic
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Fase
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-600">
                      Estado
                    </th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-600">
                      Importe
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      CPGC
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Fecha
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Tercero
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">
                      Descripción
                    </th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-600">
                      Válido
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {orphanOperations.map((op) => renderOperationRow(op))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
