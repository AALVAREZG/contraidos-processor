/**
 * Main dashboard component
 */

import React from 'react';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import { SummaryCard } from '../common/SummaryCard';
import { DetailedContraidosTable } from './DetailedContraidosTable';
import type { AnalysisResult } from '../../types';
import { formatCurrency, formatNumber } from '../../utils/formatters';

interface DashboardProps {
  analysis: AnalysisResult;
}

const COLORS = {
  green: '#10b981',
  blue: '#3b82f6',
  red: '#ef4444',
  purple: '#8b5cf6',
};

export const Dashboard: React.FC<DashboardProps> = ({ analysis }) => {
  const { summary, details, validation, chart_data } = analysis;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <SummaryCard
          title="Total Operaciones"
          value={formatNumber(summary.total_operations)}
          icon={FileText}
          color="blue"
        />
        <SummaryCard
          title="AINP (Arqueo)"
          value={formatNumber(summary.arqueo_count)}
          icon={TrendingUp}
          color="green"
        />
        <SummaryCard
          title="Balance Neto"
          value={formatCurrency(details.calculations.net_balance)}
          icon={details.calculations.net_balance >= 0 ? TrendingUp : TrendingDown}
          color={details.calculations.net_balance >= 0 ? 'green' : 'red'}
        />
        <SummaryCard
          title="Problemas"
          value={validation.total_issues}
          icon={validation.is_valid ? CheckCircle : AlertTriangle}
          color={validation.is_valid ? 'green' : 'red'}
          subtitle={`${validation.total_warnings} advertencias`}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart - Distribution by Phase */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Distribución por Fase
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chart_data.fase_distribution.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chart_data.fase_distribution.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Bar Chart - Balance Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Resumen de Balances
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chart_data.balance_summary.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip formatter={(value) => formatCurrency(Number(value))} />
              <Bar dataKey="value" fill={COLORS.blue}>
                {chart_data.balance_summary.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Validation Issues */}
      {validation.total_issues > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-600" />
            Problemas Detectados ({validation.total_issues})
          </h3>
          <div className="space-y-3">
            {validation.issues.slice(0, 5).map((issue, idx) => (
              <div
                key={idx}
                className="p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-red-900">{issue.type}</p>
                    <p className="text-sm text-red-700 mt-1">{issue.message}</p>
                    <div className="mt-2 text-xs text-red-600">
                      {issue.operation && `Operación: ${issue.operation}`}
                      {issue.amount && ` | Importe: ${formatCurrency(issue.amount)}`}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Warnings */}
      {validation.total_warnings > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            Advertencias ({validation.total_warnings})
          </h3>
          <div className="space-y-3">
            {validation.warnings.slice(0, 5).map((warning, idx) => (
              <div
                key={idx}
                className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg"
              >
                <p className="font-medium text-yellow-900">{warning.type}</p>
                <p className="text-sm text-yellow-700 mt-1">{warning.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Contraídos Table */}
      <DetailedContraidosTable
        contraidos={details.by_contraido}
        orphanOperations={details.orphan_operations}
      />
    </div>
  );
};
