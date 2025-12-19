#!/usr/bin/env python3
"""
Contraidos Analyzer Tool
Herramienta para análisis de archivos de contraídos con reglas de negocio específicas
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Operation:
    """Representa una operación individual"""
    num_operacion: int
    año: int
    aplicacion: int
    num_contraido: str
    importe: float
    cpgc: int
    fase: str
    fecha: str
    tercero: str
    descripcion: str
    estado: str
    
    @property
    def is_arqueo(self) -> bool:
        """Operación de arqueo (positiva)"""
        return self.fase == 'AINP'
    
    @property
    def is_cargo(self) -> bool:
        """Operación de cargo (negativa)"""
        return self.fase == 'M;P'
    
    @property
    def is_valid_cargo(self) -> bool:
        """Cargo válido solo si estado == 4"""
        return self.is_cargo and (self.estado == 4 or self.estado == '4')
    
    @property
    def is_invalid_cargo(self) -> bool:
        """Cargo inválido o incompleto"""
        return self.is_cargo and self.estado != 4 and self.estado != '4'
    
    @property
    def effective_amount(self) -> float:
        """Importe efectivo considerando la fase y validez"""
        if self.is_arqueo:
            return self.importe
        elif self.is_valid_cargo:
            return -self.importe
        else:
            return 0  # Operaciones inválidas no cuentan


class ContraidosAnalyzer:
    """Analizador principal de archivos de contraídos"""
    
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.df = None
        self.operations = []
        self.analysis_results = {}
        
        if filepath:
            self.load_file(filepath)
    
    def load_file(self, filepath: str) -> None:
        """Carga un archivo Excel de contraídos"""
        try:
            self.filepath = filepath
            self.df = pd.read_excel(filepath)
            self.df.columns = self.df.columns.str.strip()
            self._validate_columns()
            self._parse_operations()
            print(f"✓ Archivo cargado: {Path(filepath).name}")
            print(f"  - {len(self.df)} operaciones encontradas")
        except Exception as e:
            raise Exception(f"Error cargando archivo: {str(e)}")
    
    def _validate_columns(self) -> None:
        """Valida que el archivo tenga las columnas requeridas"""
        required_columns = [
            'Nº Operación', 'Año', 'Aplicación', 'Nº Contraido',
            'Importe', 'CPGC', 'FASE', 'Fecha', 'Tercero',
            'Descripción', 'Estado'
        ]
        missing = [col for col in required_columns if col not in self.df.columns]
        if missing:
            raise ValueError(f"Columnas faltantes: {missing}")
    
    def _parse_operations(self) -> None:
        """Convierte el DataFrame en objetos Operation"""
        self.operations = []
        for _, row in self.df.iterrows():
            # Handle Estado - convert to int if it's a numeric 4, otherwise keep as string
            estado_val = row['Estado']
            if pd.notna(estado_val):
                if isinstance(estado_val, (int, float)):
                    estado = int(estado_val)
                else:
                    try:
                        estado = int(estado_val)
                    except:
                        estado = str(estado_val).strip()
            else:
                estado = ''
            
            op = Operation(
                num_operacion=row['Nº Operación'],
                año=row['Año'],
                aplicacion=row['Aplicación'],
                num_contraido=str(row['Nº Contraido']) if pd.notna(row['Nº Contraido']) else '',
                importe=row['Importe'],
                cpgc=row['CPGC'],
                fase=row['FASE'],
                fecha=str(row['Fecha']) if pd.notna(row['Fecha']) else '',
                tercero=str(row['Tercero']) if pd.notna(row['Tercero']) else '',
                descripcion=str(row['Descripción']) if pd.notna(row['Descripción']) else '',
                estado=estado
            )
            self.operations.append(op)
    
    def analyze(self) -> Dict:
        """Ejecuta análisis completo del archivo"""
        if not self.operations:
            raise ValueError("No hay operaciones cargadas")
        
        results = {
            'summary': self._analyze_summary(),
            'by_fase': self._analyze_by_fase(),
            'by_contraido': self._analyze_by_contraido(),
            'validation': self._validate_operations(),
            'calculations': self._calculate_totals()
        }
        
        self.analysis_results = results
        return results
    
    def _analyze_summary(self) -> Dict:
        """Análisis resumen del archivo"""
        return {
            'total_operations': len(self.operations),
            'arqueo_count': sum(1 for op in self.operations if op.is_arqueo),
            'cargo_count': sum(1 for op in self.operations if op.is_cargo),
            'valid_cargo_count': sum(1 for op in self.operations if op.is_valid_cargo),
            'invalid_cargo_count': sum(1 for op in self.operations if op.is_invalid_cargo),
            'unique_contraidos': len(set(op.num_contraido for op in self.operations if op.num_contraido)),
            'date_range': self._get_date_range()
        }
    
    def _get_date_range(self) -> Dict:
        """Obtiene el rango de fechas de las operaciones"""
        valid_dates = []
        for op in self.operations:
            if op.fecha and op.fecha != 'nan':
                try:
                    # Intenta parsear diferentes formatos de fecha
                    if '00:00:00' in op.fecha:
                        date_str = op.fecha.split(' ')[0]
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                    elif '/' in op.fecha:
                        date = datetime.strptime(op.fecha, '%d/%m/%Y')
                    else:
                        continue
                    valid_dates.append(date)
                except:
                    continue
        
        if valid_dates:
            return {
                'earliest': min(valid_dates).strftime('%Y-%m-%d'),
                'latest': max(valid_dates).strftime('%Y-%m-%d')
            }
        return {'earliest': None, 'latest': None}
    
    def _analyze_by_fase(self) -> Dict:
        """Análisis agrupado por fase"""
        ainp_ops = [op for op in self.operations if op.is_arqueo]
        mp_ops = [op for op in self.operations if op.is_cargo]
        
        return {
            'AINP': {
                'count': len(ainp_ops),
                'total_amount': sum(op.importe for op in ainp_ops),
                'operations': [op.num_operacion for op in ainp_ops]
            },
            'M;P': {
                'count': len(mp_ops),
                'valid': {
                    'count': sum(1 for op in mp_ops if op.is_valid_cargo),
                    'total_amount': sum(op.importe for op in mp_ops if op.is_valid_cargo),
                    'operations': [op.num_operacion for op in mp_ops if op.is_valid_cargo]
                },
                'invalid': {
                    'count': sum(1 for op in mp_ops if op.is_invalid_cargo),
                    'total_amount': sum(op.importe for op in mp_ops if op.is_invalid_cargo),
                    'operations': [op.num_operacion for op in mp_ops if op.is_invalid_cargo]
                }
            }
        }
    
    def _analyze_by_contraido(self) -> List[Dict]:
        """Análisis agrupado por número de contraído"""
        contraido_groups = {}
        
        for op in self.operations:
            if not op.num_contraido:
                continue
            
            if op.num_contraido not in contraido_groups:
                contraido_groups[op.num_contraido] = {
                    'num_contraido': op.num_contraido,
                    'operations': [],
                    'total_arqueo': 0,
                    'total_cargo_valid': 0,
                    'total_cargo_invalid': 0,
                    'net_balance': 0,
                    'has_invalid_operations': False,
                    'needs_attention': False
                }
            
            group = contraido_groups[op.num_contraido]
            group['operations'].append({
                'num_operacion': op.num_operacion,
                'fase': op.fase,
                'estado': op.estado,
                'importe': op.importe,
                'fecha': op.fecha,
                'descripcion': op.descripcion[:50] + '...' if len(op.descripcion) > 50 else op.descripcion
            })
            
            if op.is_arqueo:
                group['total_arqueo'] += op.importe
            elif op.is_valid_cargo:
                group['total_cargo_valid'] += op.importe
            elif op.is_invalid_cargo:
                group['total_cargo_invalid'] += op.importe
                group['has_invalid_operations'] = True
                group['needs_attention'] = True
            
            group['net_balance'] = group['total_arqueo'] - group['total_cargo_valid']
        
        # Convertir a lista y ordenar por balance neto
        result = list(contraido_groups.values())
        result.sort(key=lambda x: abs(x['net_balance']), reverse=True)
        
        return result
    
    def _validate_operations(self) -> Dict:
        """Validación de operaciones según reglas de negocio"""
        issues = []
        warnings = []
        
        # Buscar operaciones M;P sin estado 4
        invalid_mp = [op for op in self.operations if op.is_invalid_cargo]
        if invalid_mp:
            for op in invalid_mp:
                issues.append({
                    'type': 'INVALID_CARGO',
                    'operation': op.num_operacion,
                    'contraido': op.num_contraido,
                    'amount': op.importe,
                    'estado': op.estado,
                    'message': f"Operación M;P con estado '{op.estado}' != 4 (incompleta/cancelada)"
                })
        
        # Buscar contraídos con balance significativo
        by_contraido = self._analyze_by_contraido()
        for group in by_contraido:
            if abs(group['net_balance']) > 0.01:  # Tolerancia para redondeo
                if group['net_balance'] > 0:
                    warnings.append({
                        'type': 'POSITIVE_BALANCE',
                        'contraido': group['num_contraido'],
                        'balance': group['net_balance'],
                        'message': f"Contraído con saldo positivo: {group['net_balance']:.2f}"
                    })
                else:
                    warnings.append({
                        'type': 'NEGATIVE_BALANCE',
                        'contraido': group['num_contraido'],
                        'balance': group['net_balance'],
                        'message': f"Contraído con saldo negativo: {group['net_balance']:.2f}"
                    })
        
        # Verificar si hay operaciones M;P sin anulación
        mp_without_cancel = []
        for op in self.operations:
            if op.is_invalid_cargo:
                # Buscar si hay otra operación M;P que anule esta
                has_cancellation = any(
                    other.is_cargo and 
                    other.num_contraido == op.num_contraido and
                    other.num_operacion != op.num_operacion and
                    'anula' in other.descripcion.lower()
                    for other in self.operations
                )
                if not has_cancellation:
                    mp_without_cancel.append(op)
        
        if mp_without_cancel:
            for op in mp_without_cancel:
                issues.append({
                    'type': 'MP_WITHOUT_CANCELLATION',
                    'operation': op.num_operacion,
                    'contraido': op.num_contraido,
                    'amount': op.importe,
                    'message': "Operación M;P inválida sin anulación detectada"
                })
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'total_issues': len(issues),
            'total_warnings': len(warnings)
        }
    
    def _calculate_totals(self) -> Dict:
        """Calcula los totales según las reglas de negocio"""
        total_arqueo = sum(op.importe for op in self.operations if op.is_arqueo)
        total_cargo_valid = sum(op.importe for op in self.operations if op.is_valid_cargo)
        total_cargo_invalid = sum(op.importe for op in self.operations if op.is_invalid_cargo)
        
        return {
            'total_arqueo_positive': total_arqueo,
            'total_cargo_negative': total_cargo_valid,
            'total_cargo_invalid': total_cargo_invalid,
            'net_balance': total_arqueo - total_cargo_valid,
            'percentage_invalid': (total_cargo_invalid / (total_cargo_valid + total_cargo_invalid) * 100) 
                                 if (total_cargo_valid + total_cargo_invalid) > 0 else 0
        }
    
    def export_analysis(self, output_path: str = None) -> str:
        """Exporta el análisis a un archivo JSON"""
        if not self.analysis_results:
            self.analyze()
        
        if not output_path:
            base_name = Path(self.filepath).stem if self.filepath else 'contraidos'
            output_path = f"{base_name}_analysis.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        return output_path
    
    def generate_report(self) -> str:
        """Genera un reporte formateado del análisis"""
        if not self.analysis_results:
            self.analyze()
        
        results = self.analysis_results
        report = []
        
        report.append("=" * 80)
        report.append("ANÁLISIS DE CONTRAÍDOS")
        report.append("=" * 80)
        
        # Resumen
        summary = results['summary']
        report.append(f"\n📊 RESUMEN")
        report.append(f"  • Total operaciones: {summary['total_operations']}")
        report.append(f"  • Operaciones AINP (arqueo): {summary['arqueo_count']}")
        report.append(f"  • Operaciones M;P (cargo): {summary['cargo_count']}")
        report.append(f"    - Válidas (estado=4): {summary['valid_cargo_count']}")
        report.append(f"    - Inválidas: {summary['invalid_cargo_count']}")
        report.append(f"  • Contraídos únicos: {summary['unique_contraidos']}")
        
        # Cálculos
        calcs = results['calculations']
        report.append(f"\n💰 TOTALES")
        report.append(f"  • Total AINP (positivo): €{calcs['total_arqueo_positive']:,.2f}")
        report.append(f"  • Total M;P válido (negativo): €{calcs['total_cargo_negative']:,.2f}")
        report.append(f"  • Total M;P inválido: €{calcs['total_cargo_invalid']:,.2f}")
        report.append(f"  • BALANCE NETO: €{calcs['net_balance']:,.2f}")
        
        # Validación
        validation = results['validation']
        report.append(f"\n⚠️  VALIDACIÓN")
        report.append(f"  • Estado: {'✓ VÁLIDO' if validation['is_valid'] else '✗ CON PROBLEMAS'}")
        report.append(f"  • Problemas encontrados: {validation['total_issues']}")
        report.append(f"  • Advertencias: {validation['total_warnings']}")
        
        if validation['issues']:
            report.append("\n  PROBLEMAS CRÍTICOS:")
            for issue in validation['issues'][:5]:  # Mostrar solo los primeros 5
                report.append(f"    - {issue['message']}")
                report.append(f"      Operación: {issue['operation']}, Importe: €{issue['amount']:.2f}")
        
        if validation['warnings']:
            report.append("\n  ADVERTENCIAS:")
            for warning in validation['warnings'][:5]:
                report.append(f"    - {warning['message']}")
        
        # Contraídos con problemas
        by_contraido = results['by_contraido']
        problematic = [c for c in by_contraido if c['needs_attention']]
        if problematic:
            report.append(f"\n🔍 CONTRAÍDOS QUE REQUIEREN ATENCIÓN")
            for contraido in problematic[:10]:
                report.append(f"\n  Contraído: {contraido['num_contraido']}")
                report.append(f"    • Balance: €{contraido['net_balance']:,.2f}")
                report.append(f"    • Operaciones: {len(contraido['operations'])}")
                if contraido['has_invalid_operations']:
                    report.append(f"    • ⚠️ Tiene operaciones inválidas")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def export_to_excel(self, output_path: str = None) -> str:
        """Exporta el análisis a un archivo Excel con múltiples hojas"""
        if not self.analysis_results:
            self.analyze()
        
        if not output_path:
            base_name = Path(self.filepath).stem if self.filepath else 'contraidos'
            output_path = f"{base_name}_analysis.xlsx"
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Hoja 1: Datos originales
            self.df.to_excel(writer, sheet_name='Datos_Originales', index=False)
            
            # Hoja 2: Resumen
            summary_data = {
                'Métrica': [
                    'Total Operaciones',
                    'Operaciones AINP',
                    'Operaciones M;P Válidas',
                    'Operaciones M;P Inválidas',
                    'Total AINP (€)',
                    'Total M;P Válido (€)',
                    'Balance Neto (€)'
                ],
                'Valor': [
                    self.analysis_results['summary']['total_operations'],
                    self.analysis_results['summary']['arqueo_count'],
                    self.analysis_results['summary']['valid_cargo_count'],
                    self.analysis_results['summary']['invalid_cargo_count'],
                    self.analysis_results['calculations']['total_arqueo_positive'],
                    self.analysis_results['calculations']['total_cargo_negative'],
                    self.analysis_results['calculations']['net_balance']
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Resumen', index=False)
            
            # Hoja 3: Análisis por Contraído
            contraido_data = []
            for group in self.analysis_results['by_contraido']:
                contraido_data.append({
                    'Nº Contraído': group['num_contraido'],
                    'Total Arqueo': group['total_arqueo'],
                    'Total Cargo Válido': group['total_cargo_valid'],
                    'Total Cargo Inválido': group['total_cargo_invalid'],
                    'Balance Neto': group['net_balance'],
                    'Nº Operaciones': len(group['operations']),
                    'Requiere Atención': 'Sí' if group['needs_attention'] else 'No'
                })
            pd.DataFrame(contraido_data).to_excel(writer, sheet_name='Por_Contraido', index=False)
            
            # Hoja 4: Problemas detectados
            issues_data = []
            for issue in self.analysis_results['validation']['issues']:
                issues_data.append({
                    'Tipo': issue['type'],
                    'Operación': issue['operation'],
                    'Contraído': issue['contraido'],
                    'Importe': issue['amount'],
                    'Descripción': issue['message']
                })
            pd.DataFrame(issues_data).to_excel(writer, sheet_name='Problemas', index=False)
        
        return output_path


def main():
    """Función principal para uso desde línea de comandos"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python contraidos_analyzer.py <archivo.xlsx>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        analyzer = ContraidosAnalyzer(filepath)
        analyzer.analyze()
        
        # Mostrar reporte
        print(analyzer.generate_report())
        
        # Exportar resultados
        json_path = analyzer.export_analysis()
        excel_path = analyzer.export_to_excel()
        
        print(f"\n✓ Análisis exportado a:")
        print(f"  - JSON: {json_path}")
        print(f"  - Excel: {excel_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
