# 📊 Portfolio Analytics Dashboard

## 🚀 Inicio Rápido

```bash
cd Client
npm install
npm run dev
```

Accede a: http://localhost:5173

## 📋 Descripción

Dashboard web para análisis de portafolios financieros con computación paralela. Incluye análisis de sentimiento social y trading intradía.

## 🎯 Funcionalidades Principales

### Análisis de Sentimiento Social

- Filtrado por engagement de redes sociales
- Ranking mensual de activos
- Visualización de retornos vs benchmark

### Trading Intradía

- Modelos GARCH para predicción de volatilidad
- Indicadores técnicos (RSI, Bandas de Bollinger)
- Señales de entrada/salida combinadas

### Benchmarking

- Comparación secuencial vs paralelo
- Métricas de performance y CPU
- Análisis de escalabilidad

## 🛠️ Stack Tecnológico

- **React 19** - Framework principal
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Estilos
- **Recharts** - Gráficos interactivos
- **FastAPI** - Backend API
- **Ray** - Computación distribuida

## 📁 Estructura del Proyecto

```
Client/
├── src/
│   ├── pages/           # Páginas principales
│   ├── components/      # Componentes reutilizables
│   └── api/            # Clientes API
├── public/             # Assets estáticos
└── package.json        # Dependencias
```

## 🔧 Scripts Disponibles

- `npm run dev` - Desarrollo local
- `npm run build` - Build de producción
- `npm run preview` - Preview del build

## 🐳 Docker

```bash
docker-compose up
```

## 📞 Soporte

Para problemas técnicos, revisa:

- Console del navegador para errores
- Logs del servidor de desarrollo
- Network tab para problemas de API

---

**Nota**: Este frontend requiere que el backend esté ejecutándose en http://localhost:8000
