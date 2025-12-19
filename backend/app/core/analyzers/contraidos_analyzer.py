"""Contraídos analyzer with business rules"""

import pandas as pd
from datetime import datetime
from typing import List, Dict
from .base import BaseAnalyzer, AnalysisResult
from ..models import Operation


class ContraidosAnalyzer(BaseAnalyzer):
    """
    Analyzer for contraídos data with specific business rules.

    Business Rules:
    - AINP (Arqueo): Positive operations (income/receipts)
    - M;P (Cargo): Negative operations, valid only when estado == 4
    - Invalid M;P operations indicate incomplete or cancelled transactions
    """

    def __init__(self, df: pd.DataFrame, metadata: dict = None):
        super().__init__(df, metadata)
        self.operations: List[Operation] = []
        self._parse_operations()

    def get_analysis_type(self) -> str:
        return "contraidos"

    @staticmethod
    def can_analyze(df: pd.DataFrame, metadata: dict = None) -> bool:
        """Check if this analyzer can handle the data"""
        required_cols = {"FASE", "Nº Operación", "Importe"}
        df_cols = set(df.columns.str.strip())
        return required_cols.issubset(df_cols)

    def _parse_operations(self) -> None:
        """Convert DataFrame rows to Operation objects"""
        self.operations = []

        for _, row in self.df.iterrows():
            # Handle Estado - convert to int if numeric, otherwise string
            estado_val = row["Estado"]
            if pd.notna(estado_val):
                if isinstance(estado_val, (int, float)):
                    estado = int(estado_val)
                else:
                    try:
                        estado = int(estado_val)
                    except:
                        estado = str(estado_val).strip()
            else:
                estado = ""

            op = Operation(
                num_operacion=row["Nº Operación"],
                año=row["Año"],
                aplicacion=row["Aplicación"],
                num_contraido=str(row["Nº Contraido"]) if pd.notna(row["Nº Contraido"]) else "",
                importe=row["Importe"],
                cpgc=row["CPGC"],
                fase=row["FASE"],
                fecha=str(row["Fecha"]) if pd.notna(row["Fecha"]) else "",
                tercero=str(row["Tercero"]) if pd.notna(row["Tercero"]) else "",
                descripcion=str(row["Descripción"]) if pd.notna(row["Descripción"]) else "",
                estado=estado,
            )
            self.operations.append(op)

    def analyze(self) -> AnalysisResult:
        """Execute complete analysis"""
        try:
            summary = self._analyze_summary()
            by_fase = self._analyze_by_fase()
            by_contraido = self._analyze_by_contraido()
            validation = self.validate_business_rules()
            calculations = self._calculate_totals()
            chart_data = self.get_chart_data()

            self.analysis_results = AnalysisResult(
                success=True,
                analysis_type="contraidos",
                summary=summary,
                details={
                    "by_fase": by_fase,
                    "by_contraido": by_contraido,
                    "calculations": calculations,
                },
                validation=validation,
                chart_data=chart_data,
                metadata=self.metadata,
            )

            return self.analysis_results

        except Exception as e:
            return AnalysisResult(
                success=False, analysis_type="contraidos", error=f"Analysis error: {str(e)}"
            )

    def _analyze_summary(self) -> Dict:
        """Generate summary statistics"""
        return {
            "total_operations": len(self.operations),
            "arqueo_count": sum(1 for op in self.operations if op.is_arqueo),
            "cargo_count": sum(1 for op in self.operations if op.is_cargo),
            "valid_cargo_count": sum(1 for op in self.operations if op.is_valid_cargo),
            "invalid_cargo_count": sum(1 for op in self.operations if op.is_invalid_cargo),
            "unique_contraidos": len(set(op.num_contraido for op in self.operations if op.num_contraido)),
            "date_range": self._get_date_range(),
        }

    def _get_date_range(self) -> Dict:
        """Get date range of operations"""
        valid_dates = []
        for op in self.operations:
            if op.fecha and op.fecha != "nan":
                try:
                    if "00:00:00" in op.fecha:
                        date_str = op.fecha.split(" ")[0]
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                    elif "/" in op.fecha:
                        date = datetime.strptime(op.fecha, "%d/%m/%Y")
                    else:
                        continue
                    valid_dates.append(date)
                except:
                    continue

        if valid_dates:
            return {
                "earliest": min(valid_dates).strftime("%Y-%m-%d"),
                "latest": max(valid_dates).strftime("%Y-%m-%d"),
            }
        return {"earliest": None, "latest": None}

    def _analyze_by_fase(self) -> Dict:
        """Analyze grouped by fase"""
        ainp_ops = [op for op in self.operations if op.is_arqueo]
        mp_ops = [op for op in self.operations if op.is_cargo]

        return {
            "AINP": {
                "count": len(ainp_ops),
                "total_amount": sum(op.importe for op in ainp_ops),
                "operations": [op.num_operacion for op in ainp_ops],
            },
            "M;P": {
                "count": len(mp_ops),
                "valid": {
                    "count": sum(1 for op in mp_ops if op.is_valid_cargo),
                    "total_amount": sum(op.importe for op in mp_ops if op.is_valid_cargo),
                    "operations": [op.num_operacion for op in mp_ops if op.is_valid_cargo],
                },
                "invalid": {
                    "count": sum(1 for op in mp_ops if op.is_invalid_cargo),
                    "total_amount": sum(op.importe for op in mp_ops if op.is_invalid_cargo),
                    "operations": [op.num_operacion for op in mp_ops if op.is_invalid_cargo],
                },
            },
        }

    def _analyze_by_contraido(self) -> List[Dict]:
        """Analyze grouped by contraído number"""
        contraido_groups = {}

        for op in self.operations:
            if not op.num_contraido:
                continue

            if op.num_contraido not in contraido_groups:
                contraido_groups[op.num_contraido] = {
                    "num_contraido": op.num_contraido,
                    "operations": [],
                    "total_arqueo": 0,
                    "total_cargo_valid": 0,
                    "total_cargo_invalid": 0,
                    "net_balance": 0,
                    "has_invalid_operations": False,
                    "needs_attention": False,
                }

            group = contraido_groups[op.num_contraido]
            group["operations"].append(
                {
                    "num_operacion": op.num_operacion,
                    "fase": op.fase,
                    "estado": op.estado,
                    "importe": op.importe,
                    "fecha": op.fecha,
                    "descripcion": op.descripcion[:50] + "..." if len(op.descripcion) > 50 else op.descripcion,
                }
            )

            if op.is_arqueo:
                group["total_arqueo"] += op.importe
            elif op.is_valid_cargo:
                group["total_cargo_valid"] += op.importe
            elif op.is_invalid_cargo:
                group["total_cargo_invalid"] += op.importe
                group["has_invalid_operations"] = True
                group["needs_attention"] = True

            group["net_balance"] = group["total_arqueo"] - group["total_cargo_valid"]

        # Convert to list and sort by balance
        result = list(contraido_groups.values())
        result.sort(key=lambda x: abs(x["net_balance"]), reverse=True)

        return result

    def _calculate_totals(self) -> Dict:
        """Calculate totals according to business rules"""
        total_arqueo = sum(op.importe for op in self.operations if op.is_arqueo)
        total_cargo_valid = sum(op.importe for op in self.operations if op.is_valid_cargo)
        total_cargo_invalid = sum(op.importe for op in self.operations if op.is_invalid_cargo)

        return {
            "total_arqueo_positive": total_arqueo,
            "total_cargo_negative": total_cargo_valid,
            "total_cargo_invalid": total_cargo_invalid,
            "net_balance": total_arqueo - total_cargo_valid,
            "percentage_invalid": (total_cargo_invalid / (total_cargo_valid + total_cargo_invalid) * 100)
            if (total_cargo_valid + total_cargo_invalid) > 0
            else 0,
        }

    def validate_business_rules(self) -> Dict:
        """Validate operations according to business rules"""
        issues = []
        warnings = []

        # Find invalid M;P operations (estado != 4)
        invalid_mp = [op for op in self.operations if op.is_invalid_cargo]
        if invalid_mp:
            for op in invalid_mp:
                issues.append(
                    {
                        "type": "INVALID_CARGO",
                        "severity": "critical",
                        "operation": op.num_operacion,
                        "contraido": op.num_contraido,
                        "amount": op.importe,
                        "estado": op.estado,
                        "message": f"Operación M;P con estado '{op.estado}' != 4 (incompleta/cancelada)",
                    }
                )

        # Find contraídos with significant balance
        by_contraido = self._analyze_by_contraido()
        for group in by_contraido:
            if abs(group["net_balance"]) > 0.01:  # Tolerance for rounding
                severity = "warning"
                if group["net_balance"] > 0:
                    warnings.append(
                        {
                            "type": "POSITIVE_BALANCE",
                            "severity": severity,
                            "contraido": group["num_contraido"],
                            "balance": group["net_balance"],
                            "message": f"Contraído con saldo positivo: €{group['net_balance']:.2f}",
                        }
                    )
                else:
                    warnings.append(
                        {
                            "type": "NEGATIVE_BALANCE",
                            "severity": severity,
                            "contraido": group["num_contraido"],
                            "balance": group["net_balance"],
                            "message": f"Contraído con saldo negativo: €{group['net_balance']:.2f}",
                        }
                    )

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_issues": len(issues),
            "total_warnings": len(warnings),
        }

    def get_chart_data(self) -> Dict:
        """Get data formatted for charts"""
        by_fase = self._analyze_by_fase()
        calculations = self._calculate_totals()

        return {
            "fase_distribution": {
                "type": "pie",
                "title": "Distribución por Fase",
                "data": [
                    {"name": "AINP (Arqueo)", "value": by_fase["AINP"]["count"], "color": "#10b981"},
                    {
                        "name": "M;P Válido",
                        "value": by_fase["M;P"]["valid"]["count"],
                        "color": "#3b82f6",
                    },
                    {
                        "name": "M;P Inválido",
                        "value": by_fase["M;P"]["invalid"]["count"],
                        "color": "#ef4444",
                    },
                ],
            },
            "balance_summary": {
                "type": "bar",
                "title": "Resumen de Balances",
                "data": [
                    {
                        "category": "AINP Total",
                        "value": calculations["total_arqueo_positive"],
                        "color": "#10b981",
                    },
                    {
                        "category": "M;P Válido",
                        "value": calculations["total_cargo_negative"],
                        "color": "#3b82f6",
                    },
                    {
                        "category": "Balance Neto",
                        "value": calculations["net_balance"],
                        "color": "#8b5cf6",
                    },
                ],
            },
            "top_contraidos": {
                "type": "bar",
                "title": "Top 10 Contraídos por Balance",
                "data": [
                    {"contraido": c["num_contraido"], "balance": c["net_balance"]}
                    for c in self._analyze_by_contraido()[:10]
                ],
            },
        }
