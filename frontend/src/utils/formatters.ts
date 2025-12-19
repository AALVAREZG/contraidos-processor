/**
 * Utility functions for formatting data
 */

/**
 * Format currency in EUR
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: 'EUR',
  }).format(amount);
};

/**
 * Format number with thousands separator
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('es-ES').format(num);
};

/**
 * Format date
 */
export const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return new Intl.DateFormat('es-ES').format(date);
  } catch {
    return dateString;
  }
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number): string => {
  return `${value.toFixed(2)}%`;
};

/**
 * Get status color based on value
 */
export const getStatusColor = (isValid: boolean): string => {
  return isValid ? 'text-green-600' : 'text-red-600';
};

/**
 * Get severity color
 */
export const getSeverityColor = (severity: string): string => {
  switch (severity) {
    case 'critical':
      return 'text-red-600 bg-red-50';
    case 'warning':
      return 'text-yellow-600 bg-yellow-50';
    default:
      return 'text-blue-600 bg-blue-50';
  }
};
