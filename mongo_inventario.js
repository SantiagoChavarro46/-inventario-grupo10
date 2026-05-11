// ============================================================
//  SISTEMA DE INVENTARIO -- MongoDB
//  Grupo 10: Santiago Chavarro & Juan Pablo Sánchez
//  Ejecutar en: mongosh  ó  MongoDB Compass > Open Shell
// ============================================================

// 1. SELECCIONAR / CREAR LA BASE DE DATOS
use inventario_db;

// ============================================================
// COLECCIÓN 1: lotes_produccion
// Guarda cada lote fabricado de un producto.
// producto_id hace referencia al id de la tabla producto en PG.
// ============================================================

db.createCollection("lotes_produccion", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["producto_id", "fecha", "cantidad_producida"],
      properties: {
        producto_id: {
          bsonType: "int",
          description: "ID del producto en PostgreSQL (requerido)"
        },
        fecha: {
          bsonType: "date",
          description: "Fecha del lote (requerida)"
        },
        cantidad_producida: {
          bsonType: "int",
          minimum: 1,
          description: "Cantidad producida, mínimo 1 (requerida)"
        },
        calidad: {
          bsonType: "string",
          enum: ["alta", "media", "baja"],
          description: "Nivel de calidad del lote"
        },
        origen: {
          bsonType: "string",
          description: "Origen o proveedor de la materia prima"
        },
        notas: {
          bsonType: "string",
          description: "Observaciones libres del lote"
        },
        datos_variables: {
          bsonType: "object",
          description: "Campos extra que varían por tipo de producto"
        }
      }
    }
  }
});

// Índices para lotes_produccion
db.lotes_produccion.createIndex({ producto_id: 1 });
db.lotes_produccion.createIndex({ fecha: -1 });
db.lotes_produccion.createIndex({ producto_id: 1, fecha: -1 });

// ── Datos de prueba ──────────────────────────────────────────
db.lotes_produccion.insertMany([
  {
    producto_id: 1,
    fecha: new Date("2025-01-10"),
    cantidad_producida: 200,
    calidad: "alta",
    origen: "Proveedor Norte",
    notas: "Lote sin observaciones",
    datos_variables: {
      temperatura_almacen: "18°C",
      humedad: "60%"
    }
  },
  {
    producto_id: 1,
    fecha: new Date("2025-02-15"),
    cantidad_producida: 150,
    calidad: "media",
    origen: "Proveedor Sur",
    notas: "Ligero retraso en entrega",
    datos_variables: {
      temperatura_almacen: "20°C",
      humedad: "65%"
    }
  },
  {
    producto_id: 2,
    fecha: new Date("2025-03-01"),
    cantidad_producida: 100,
    calidad: "alta",
    origen: "Proveedor Central",
    notas: "",
    datos_variables: {
      lote_certificado: true,
      codigo_trazabilidad: "CERT-2025-0301"
    }
  }
]);

// ============================================================
// COLECCIÓN 2: eventos_historial
// Log inmutable de acciones importantes del sistema.
// referencia_id apunta al id del registro en PG que generó el evento.
// ============================================================

db.createCollection("eventos_historial", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["tipo", "fecha", "descripcion"],
      properties: {
        tipo: {
          bsonType: "string",
          enum: ["produccion", "venta", "ajuste_inventario", "devolucion", "alerta_stock"],
          description: "Tipo de evento (requerido)"
        },
        fecha: {
          bsonType: "date",
          description: "Fecha y hora del evento (requerida)"
        },
        descripcion: {
          bsonType: "string",
          description: "Descripción legible del evento (requerida)"
        },
        referencia_id: {
          bsonType: "int",
          description: "ID del registro en PostgreSQL que originó el evento"
        },
        producto_id: {
          bsonType: "int",
          description: "ID del producto involucrado (referencia a PG)"
        },
        usuario_id: {
          bsonType: "int",
          description: "ID del usuario que realizó la acción (referencia a PG)"
        },
        metadata: {
          bsonType: "object",
          description: "Datos adicionales del evento (flexible)"
        }
      }
    }
  }
});

// Índices para eventos_historial
db.eventos_historial.createIndex({ tipo: 1 });
db.eventos_historial.createIndex({ fecha: -1 });
db.eventos_historial.createIndex({ producto_id: 1, fecha: -1 });
db.eventos_historial.createIndex({ referencia_id: 1 });

// ── Datos de prueba ──────────────────────────────────────────
db.eventos_historial.insertMany([
  {
    tipo: "produccion",
    fecha: new Date("2025-01-10T08:00:00"),
    descripcion: "Lote de 200 unidades del Producto A registrado",
    producto_id: 1,
    usuario_id: 1,
    metadata: {
      lote_id: "lote_ref_aqui",
      cantidad: 200
    }
  },
  {
    tipo: "venta",
    fecha: new Date("2025-01-20T14:30:00"),
    descripcion: "Venta #1 completada por $62.000",
    referencia_id: 1,   // id de venta en PostgreSQL
    usuario_id: 1,
    metadata: {
      cliente: "Juan Pérez",
      total: 62000,
      productos: [
        { producto_id: 1, cantidad: 2 },
        { producto_id: 2, cantidad: 1 }
      ]
    }
  },
  {
    tipo: "ajuste_inventario",
    fecha: new Date("2025-02-01T09:15:00"),
    descripcion: "Ajuste manual: +30 unidades Producto C por conteo físico",
    producto_id: 3,
    usuario_id: 2,
    metadata: {
      cantidad_anterior: 170,
      cantidad_nueva: 200,
      motivo: "Diferencia en conteo físico"
    }
  },
  {
    tipo: "alerta_stock",
    fecha: new Date("2025-02-10T07:00:00"),
    descripcion: "Stock del Producto B bajó del mínimo (5 unidades)",
    producto_id: 2,
    metadata: {
      cantidad_actual: 4,
      cantidad_minima: 5
    }
  }
]);

// ============================================================
// CONSULTAS ÚTILES PARA REPORTES
// ============================================================

// -- Historial de producción de un producto específico
db.lotes_produccion.find(
  { producto_id: 1 },
  { fecha: 1, cantidad_producida: 1, calidad: 1, _id: 0 }
).sort({ fecha: -1 });

// -- Total producido por producto
db.lotes_produccion.aggregate([
  {
    $group: {
      _id: "$producto_id",
      total_producido: { $sum: "$cantidad_producida" },
      lotes: { $count: {} }
    }
  },
  { $sort: { total_producido: -1 } }
]);

// -- Eventos de los últimos 30 días
db.eventos_historial.find({
  fecha: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
}).sort({ fecha: -1 });

// -- Alertas de stock sin resolver
db.eventos_historial.find(
  { tipo: "alerta_stock" },
  { descripcion: 1, fecha: 1, "metadata.cantidad_actual": 1, _id: 0 }
).sort({ fecha: -1 });

// -- Eventos agrupados por tipo
db.eventos_historial.aggregate([
  {
    $group: {
      _id: "$tipo",
      total: { $count: {} },
      ultimo_evento: { $max: "$fecha" }
    }
  }
]);
