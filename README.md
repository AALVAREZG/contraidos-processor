# 📊 Analizador de Contraídos

Herramienta profesional para el análisis de archivos de contraídos con validación automática de reglas de negocio.

## 🌟 Características

- ✅ **Validación automática** de reglas de negocio
- 📈 **Análisis por fase** (AINP vs M;P)
- 💰 **Cálculo de balances** automático
- ⚠️ **Detección de problemas** y operaciones inválidas



## 📋 Reglas de Negocio Implementadas

### Operaciones AINP (Arqueo)
- Se consideran operaciones **positivas**
- Representan ingresos o cobros

### Operaciones M;P (Cargo)
- Se consideran operaciones **negativas**
- Solo son válidas si `estado == 4`
- Estados diferentes a 4 indican operaciones incompletas o canceladas
- Se detectan automáticamente operaciones M;P sin anulación

