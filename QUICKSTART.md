# ⚡ QUICK START - Proyecto LSP

## 🚀 Inicio Rápido en 3 Pasos

### 1️⃣ Instalar (3 minutos)

```powershell
cd modelo_lstm_lsp-main
.\setup.ps1
```

### 2️⃣ Probar (30 segundos)

```powershell
python main.py
```

### 3️⃣ ¡Hacer señas frente a la cámara!

---

## 📦 ¿Qué hace este proyecto?

Traduce **Lengua de Señas Peruana** a texto y voz en tiempo real usando IA.

**14 palabras disponibles:**
- Saludos: hola, buenos días, buenas tardes, buenas noches, adiós
- Estados: bien, mal, más o menos  
- Cortesía: gracias, por favor, disculpa, me ayudas
- Preguntas: cómo estás

---

## 🎯 Comandos Esenciales

```powershell
# Interfaz gráfica
python main.py

# Modo consola
python evaluate_model.py

# Entrenar nuevo modelo
python training_model.py

# Capturar nuevas palabras
python capture_samples.py
```

---

## ⚙️ Personalizar

Edita `config.yaml`:

```yaml
# Cambiar parámetros
model:
  frames: 20  # Cambiar cantidad de frames

# Agregar palabra
vocabulary:
  word_ids:
    - "tu_palabra"
```

---

## 📚 Documentación Completa

- **README_UPDATED.md** - Todo sobre el proyecto
- **MIGRATION_GUIDE.md** - Guía de migración
- **REFACTORING_SUMMARY.md** - Resumen de cambios

---

## 🐛 Problemas?

```powershell
# Error con protobuf
pip install protobuf==3.20.3 --force-reinstall

# Error con config
pip install PyYAML

# Reinstalar todo
pip install -r requirements.txt --force-reinstall
```

Más en: `MIGRATION_GUIDE.md`

---

## 🎓 Workflow Completo

```
1. Capturar      → capture_samples.py
2. Normalizar    → normalize_samples.py  
3. Keypoints     → create_keypoints.py
4. Entrenar      → training_model.py
5. Evaluar       → evaluate_model.py
6. Usar          → main.py
```

---

**¿Listo?** → `.\setup.ps1` 🚀
