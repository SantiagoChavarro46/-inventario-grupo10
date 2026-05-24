#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║   DEMO — Arquitectura de Persistencia Políglota                  ║
║   Sistema de Gestión de Inventario Rural                         ║
║   PostgreSQL (ACID) + MongoDB (BASE/CAP)                         ║
║   Grupo 10: Santiago Chavarro & Juan Pablo Sánchez               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import sys
import datetime
import argparse
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    from rich.rule import Rule
    from rich.syntax import Syntax
    from rich.padding import Padding
    from rich.align import Align
    from rich.prompt import Prompt, Confirm
except ImportError:
    print("[ERROR] Instala rich:  pip install rich")
    sys.exit(1)

console = Console()

# ── Argumentos ─────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--pg-dsn",    default="postgresql://postgres:postgres@localhost:5432/inventario_db")
parser.add_argument("--mongo-uri", default="mongodb://localhost:27017/")
parser.add_argument("--html",      action="store_true")
args = parser.parse_args()

PG_CONN  = None
MONGO_DB = None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  UTILIDADES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def ok(m):   console.print(f"  [bold green]✔[/bold green]  {m}")
def err(m):  console.print(f"  [bold red]✘[/bold red]  {m}")
def info(m): console.print(f"  [bold cyan]→[/bold cyan]  {m}")
def warn(m): console.print(f"  [bold yellow]⚠[/bold yellow]  {m}")

def section(title, color="cyan", icon="●"):
    console.print()
    console.print(Rule(f"[bold {color}]{icon}  {title}[/bold {color}]", style=color))
    console.print()

def pausar():
    console.print()
    Prompt.ask("  [dim]Presiona Enter para continuar[/dim]", default="")

TIPO_COLOR = {
    "produccion":        "green",
    "venta":             "blue",
    "ajuste_inventario": "yellow",
    "devolucion":        "magenta",
    "alerta_stock":      "red",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  CONEXIONES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def conectar():
    global PG_CONN, MONGO_DB
    console.print()

    # PostgreSQL
    try:
        import psycopg2, psycopg2.extras
        with Progress(SpinnerColumn(), TextColumn("[cyan]{task.description}"),
                      transient=True, console=console) as p:
            p.add_task("Conectando a PostgreSQL…")
            PG_CONN = psycopg2.connect(args.pg_dsn)
        ok(f"PostgreSQL conectado  [dim]{args.pg_dsn}[/dim]")
    except Exception as e:
        err(f"PostgreSQL: {e}")
        PG_CONN = None

    # MongoDB
    try:
        from pymongo import MongoClient
        with Progress(SpinnerColumn(), TextColumn("[green]{task.description}"),
                      transient=True, console=console) as p:
            p.add_task("Conectando a MongoDB…")
            client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            MONGO_DB = client["inventario_db"]
        ok(f"MongoDB conectado     [dim]{args.mongo_uri}[/dim]")
    except Exception as e:
        err(f"MongoDB: {e}")
        MONGO_DB = None

    console.print()

def cur():
    import psycopg2.extras
    return PG_CONN.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SPLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def splash():
    console.clear()
    console.print()
    banner = Text()
    banner.append("  ██████╗  ██████╗ ██╗     ██╗ ██████╗ ██╗      ██████╗ ████████╗ █████╗ \n", style="bold cyan")
    banner.append("  ██╔══██╗██╔═══██╗██║     ██║██╔════╝ ██║     ██╔═══██╗╚══██╔══╝██╔══██╗\n", style="bold cyan")
    banner.append("  ██████╔╝██║   ██║██║     ██║██║  ███╗██║     ██║   ██║   ██║   ███████║\n", style="bold blue")
    banner.append("  ██╔═══╝ ██║   ██║██║     ██║██║   ██║██║     ██║   ██║   ██║   ██╔══██║\n", style="bold blue")
    banner.append("  ██║     ╚██████╔╝███████╗██║╚██████╔╝███████╗╚██████╔╝   ██║   ██║  ██║\n", style="bold magenta")
    banner.append("  ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝\n", style="bold magenta")
    console.print(Align.center(banner))
    console.print(Align.center(Text("🗄  Sistema de Inventario Rural — Persistencia Políglota", style="bold white")))
    console.print(Align.center(Text("PostgreSQL (ACID · CP)  +  MongoDB (BASE · AP)", style="dim")))
    console.print(Align.center(Text("Grupo 10 · Santiago Chavarro & Juan Pablo Sánchez\n", style="dim")))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MENÚ PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_principal():
    while True:
        console.print()
        console.print(Rule("[bold white]MENÚ PRINCIPAL[/bold white]", style="bright_black"))
        console.print()

        t = Table(box=box.ROUNDED, border_style="bright_black", show_header=False, padding=(0,2))
        t.add_column(width=4,  style="bold cyan",   justify="right")
        t.add_column(width=35, style="white")
        t.add_column(style="dim")

        t.add_row("1", "🐘  PostgreSQL — Consultas",      "Ver productos, clientes, ventas, inventario")
        t.add_row("2", "🐘  PostgreSQL — Insertar",        "Agregar producto, cliente o venta")
        t.add_row("3", "🐘  PostgreSQL — Actualizar",      "Modificar stock o estado de venta")
        t.add_row("4", "🐘  PostgreSQL — Eliminar",        "Eliminar registros")
        t.add_row("5", "⚡  Demo Trigger ACID",            "Probar atomicidad del stock en vivo")
        t.add_row("6", "🍃  MongoDB — Consultas",          "Ver lotes y eventos del historial")
        t.add_row("7", "🍃  MongoDB — Insertar",           "Agregar lote de producción o evento")
        t.add_row("8", "🍃  MongoDB — Eliminar",           "Eliminar documentos de colecciones")
        t.add_row("9", "🏛  Resumen Arquitectura",         "Trade-offs ACID vs BASE/CAP")
        t.add_row("H", "🌐  Generar Dashboard HTML",       "Exportar resultados al navegador")
        t.add_row("0", "🚪  Salir",                        "")

        console.print(Padding(t, (0, 4)))
        console.print()

        op = Prompt.ask("  [bold cyan]Elige una opción[/bold cyan]").strip().upper()

        if   op == "1": menu_pg_consultas()
        elif op == "2": menu_pg_insertar()
        elif op == "3": menu_pg_actualizar()
        elif op == "4": menu_pg_eliminar()
        elif op == "5": demo_trigger()
        elif op == "6": menu_mongo_consultas()
        elif op == "7": menu_mongo_insertar()
        elif op == "8": menu_mongo_eliminar()
        elif op == "9": resumen_arquitectura()
        elif op == "H": generar_html()
        elif op == "0":
            console.print("\n  [bold]¡Hasta luego![/bold] 👋\n")
            break
        else:
            warn("Opción no válida")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POSTGRESQL — CONSULTAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_pg_consultas():
    if not PG_CONN:
        err("Sin conexión a PostgreSQL"); return
    while True:
        section("PostgreSQL — Consultas", "cyan", "🐘")
        console.print("  [cyan]1[/cyan] Productos e inventario")
        console.print("  [cyan]2[/cyan] Clientes")
        console.print("  [cyan]3[/cyan] Ventas recientes")
        console.print("  [cyan]4[/cyan] Detalle de una venta")
        console.print("  [cyan]5[/cyan] Alertas de stock bajo")
        console.print("  [cyan]0[/cyan] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": pg_ver_productos()
        elif op == "2": pg_ver_clientes()
        elif op == "3": pg_ver_ventas()
        elif op == "4": pg_ver_detalle_venta()
        elif op == "5": pg_alertas_stock()
        elif op == "0": break
        else: warn("Opción no válida")

def pg_ver_productos():
    section("Productos e Inventario", "cyan", "📦")
    c = cur()
    c.execute("""
        SELECT p.id, p.nombre, p.precio, i.cantidad AS stock, i.cantidad_minima AS minimo
        FROM producto p JOIN inventario i ON i.producto_id = p.id
        ORDER BY p.id
    """)
    rows = c.fetchall()
    t = Table(box=box.ROUNDED, border_style="cyan", header_style="bold white on dark_cyan", show_lines=True)
    t.add_column("ID",      justify="right", style="dim", width=4)
    t.add_column("Producto", style="bold white")
    t.add_column("Precio",  justify="right", style="bold green")
    t.add_column("Stock",   justify="center")
    t.add_column("Mínimo",  justify="center", style="dim")
    for r in rows:
        stk = Text(str(r["stock"]), style="bold red" if r["stock"] <= r["minimo"] else "bold bright_green")
        t.add_row(str(r["id"]), r["nombre"], f"${r['precio']:,.0f}", stk, str(r["minimo"]))
    console.print(Padding(t, (0,4)))
    c.close()
    pausar()

def pg_ver_clientes():
    section("Clientes Registrados", "cyan", "👥")
    c = cur()
    c.execute("SELECT id, nombre, email, telefono FROM cliente ORDER BY id")
    rows = c.fetchall()
    t = Table(box=box.SIMPLE_HEAD, border_style="cyan", header_style="bold cyan", show_lines=False)
    t.add_column("ID",       justify="right", style="dim", width=4)
    t.add_column("Nombre",   style="bold white")
    t.add_column("Email",    style="dim")
    t.add_column("Teléfono", style="dim")
    for r in rows:
        t.add_row(str(r["id"]), r["nombre"], r["email"] or "—", r["telefono"] or "—")
    console.print(Padding(t, (0,4)))
    c.close()
    pausar()

def pg_ver_ventas():
    section("Ventas Recientes", "cyan", "💳")
    c = cur()
    c.execute("""
        SELECT v.id, cl.nombre AS cliente, v.fecha::date, v.total, v.estado
        FROM venta v JOIN cliente cl ON cl.id = v.cliente_id
        ORDER BY v.fecha DESC LIMIT 10
    """)
    rows = c.fetchall()
    t = Table(box=box.HEAVY_HEAD, border_style="magenta", header_style="bold white on dark_magenta", show_lines=True)
    t.add_column("ID",      justify="right", style="dim", width=4)
    t.add_column("Cliente", style="bold white")
    t.add_column("Fecha",   style="bright_black")
    t.add_column("Total",   justify="right", style="bold green")
    t.add_column("Estado",  justify="center")
    EST = {"completada": "bold green", "pendiente": "bold yellow", "cancelada": "bold red"}
    for r in rows:
        t.add_row(str(r["id"]), r["cliente"], str(r["fecha"]),
                  f"${r['total']:,.0f}", Text(r["estado"], style=EST.get(r["estado"],"white")))
    console.print(Padding(t, (0,4)))
    c.close()
    pausar()

def pg_ver_detalle_venta():
    section("Detalle de Venta", "cyan", "🔍")
    vid = Prompt.ask("  ID de la venta").strip()
    c = cur()
    c.execute("""
        SELECT p.nombre, dv.cantidad, dv.precio_unitario,
               dv.cantidad * dv.precio_unitario AS subtotal
        FROM detalle_venta dv JOIN producto p ON p.id = dv.producto_id
        WHERE dv.venta_id = %s
    """, (vid,))
    rows = c.fetchall()
    if not rows:
        warn(f"No se encontró la venta #{vid}"); c.close(); pausar(); return
    t = Table(title=f"Venta #{vid}", box=box.ROUNDED, border_style="cyan",
              header_style="bold cyan", show_lines=True)
    t.add_column("Producto",       style="white")
    t.add_column("Cantidad",       justify="center")
    t.add_column("Precio Unit.",   justify="right", style="dim")
    t.add_column("Subtotal",       justify="right", style="bold green")
    total = 0
    for r in rows:
        t.add_row(r["nombre"], str(r["cantidad"]),
                  f"${r['precio_unitario']:,.0f}", f"${r['subtotal']:,.0f}")
        total += r["subtotal"]
    t.add_section()
    t.add_row("", "", "[bold]TOTAL[/bold]", f"[bold green]${total:,.0f}[/bold green]")
    console.print(Padding(t, (0,4)))
    c.close()
    pausar()

def pg_alertas_stock():
    section("Alertas de Stock Bajo", "yellow", "🔔")
    c = cur()
    c.execute("""
        SELECT p.nombre, i.cantidad, i.cantidad_minima,
               i.cantidad_minima - i.cantidad AS faltante
        FROM inventario i JOIN producto p ON p.id = i.producto_id
        WHERE i.cantidad <= i.cantidad_minima
        ORDER BY faltante DESC
    """)
    rows = c.fetchall()
    if not rows:
        ok("Todos los productos tienen stock suficiente ✔")
        c.close(); pausar(); return
    t = Table(box=box.ROUNDED, border_style="yellow", header_style="bold yellow", show_lines=True)
    t.add_column("Producto",  style="white")
    t.add_column("Stock",     justify="center", style="bold red")
    t.add_column("Mínimo",   justify="center", style="dim")
    t.add_column("Faltante", justify="center", style="bold red")
    for r in rows:
        t.add_row(r["nombre"], str(r["cantidad"]),
                  str(r["cantidad_minima"]), f"-{r['faltante']} kg")
    console.print(Padding(t, (0,4)))
    c.close()
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POSTGRESQL — INSERTAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_pg_insertar():
    if not PG_CONN: err("Sin conexión a PostgreSQL"); return
    while True:
        section("PostgreSQL — Insertar", "green", "➕")
        console.print("  [green]1[/green] Nuevo producto")
        console.print("  [green]2[/green] Nuevo cliente")
        console.print("  [green]3[/green] Nueva venta")
        console.print("  [green]0[/green] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": pg_insertar_producto()
        elif op == "2": pg_insertar_cliente()
        elif op == "3": pg_insertar_venta()
        elif op == "0": break
        else: warn("Opción no válida")

def pg_insertar_producto():
    section("Nuevo Producto", "green", "📦")
    nombre = Prompt.ask("  Nombre del producto")
    desc   = Prompt.ask("  Descripción")
    precio = Prompt.ask("  Precio (COP)")
    stock  = Prompt.ask("  Stock inicial (kg/unidades)")
    minimo = Prompt.ask("  Stock mínimo")
    try:
        c = cur()
        c.execute("INSERT INTO producto (usuario_id, nombre, descripcion, precio) VALUES (1,%s,%s,%s) RETURNING id",
                  (nombre, desc, float(precio)))
        pid = c.fetchone()["id"]
        c.execute("INSERT INTO inventario (producto_id, cantidad, cantidad_minima) VALUES (%s,%s,%s)",
                  (pid, int(stock), int(minimo)))
        PG_CONN.commit()
        ok(f"Producto '[bold]{nombre}[/bold]' creado con ID [cyan]{pid}[/cyan] y stock inicial {stock}")
        c.close()
    except Exception as e:
        PG_CONN.rollback()
        err(f"Error: {e}")
    pausar()

def pg_insertar_cliente():
    section("Nuevo Cliente", "green", "👤")
    nombre = Prompt.ask("  Nombre")
    email  = Prompt.ask("  Email (opcional)", default="")
    tel    = Prompt.ask("  Teléfono (opcional)", default="")
    try:
        c = cur()
        c.execute("INSERT INTO cliente (nombre, email, telefono) VALUES (%s,%s,%s) RETURNING id",
                  (nombre, email or None, tel or None))
        cid = c.fetchone()["id"]
        PG_CONN.commit()
        ok(f"Cliente '[bold]{nombre}[/bold]' creado con ID [cyan]{cid}[/cyan]")
        c.close()
    except Exception as e:
        PG_CONN.rollback()
        err(f"Error: {e}")
    pausar()

def pg_insertar_venta():
    section("Nueva Venta", "green", "💳")
    pg_ver_clientes()
    cid = Prompt.ask("  ID del cliente")
    pg_ver_productos()

    items = []
    while True:
        pid = Prompt.ask("  ID producto a agregar (Enter para terminar)", default="")
        if not pid: break
        qty = Prompt.ask("  Cantidad (kg/unidades)")
        c = cur()
        c.execute("SELECT nombre, precio FROM producto WHERE id=%s", (pid,))
        prod = c.fetchone()
        c.close()
        if not prod:
            warn(f"Producto {pid} no encontrado"); continue
        items.append({"pid": int(pid), "nombre": prod["nombre"],
                      "qty": int(qty), "precio": float(prod["precio"])})
        ok(f"Agregado: {prod['nombre']} x{qty}")

    if not items:
        warn("No se agregaron productos"); return

    try:
        c = cur()
        c.execute("INSERT INTO venta (cliente_id, estado) VALUES (%s,'completada') RETURNING id", (cid,))
        vid = c.fetchone()["id"]
        for it in items:
            c.execute("INSERT INTO detalle_venta (venta_id, producto_id, cantidad, precio_unitario) VALUES (%s,%s,%s,%s)",
                      (vid, it["pid"], it["qty"], it["precio"]))
        PG_CONN.commit()
        ok(f"Venta [cyan]#{vid}[/cyan] registrada exitosamente")
        ok("Los triggers calcularon el total y descontaron el stock automáticamente ⚡")
        c.close()

        # registrar evento en MongoDB
        if MONGO_DB is not None:
            MONGO_DB.eventos_historial.insert_one({
                "tipo": "venta",
                "fecha": datetime.datetime.now(),
                "descripcion": f"Venta #{vid} completada desde demo interactivo",
                "referencia_id": vid,
                "usuario_id": 1,
                "metadata": {
                    "productos_vendidos": [{"producto_id": i["pid"], "nombre": i["nombre"],
                                           "cantidad": i["qty"]} for i in items]
                }
            })
            ok("Evento registrado en MongoDB (eventos_historial) 🍃")
    except Exception as e:
        PG_CONN.rollback()
        err(f"Error (ROLLBACK aplicado): {e}")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POSTGRESQL — ACTUALIZAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_pg_actualizar():
    if not PG_CONN: err("Sin conexión a PostgreSQL"); return
    while True:
        section("PostgreSQL — Actualizar", "yellow", "✏️")
        console.print("  [yellow]1[/yellow] Ajustar stock de un producto")
        console.print("  [yellow]2[/yellow] Cambiar estado de una venta")
        console.print("  [yellow]3[/yellow] Cambiar precio de un producto")
        console.print("  [yellow]0[/yellow] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": pg_ajustar_stock()
        elif op == "2": pg_cambiar_estado_venta()
        elif op == "3": pg_cambiar_precio()
        elif op == "0": break
        else: warn("Opción no válida")

def pg_ajustar_stock():
    section("Ajustar Stock", "yellow", "🔧")
    pg_ver_productos()
    pid      = Prompt.ask("  ID del producto")
    cantidad = Prompt.ask("  Nueva cantidad en stock")
    try:
        c = cur()
        c.execute("SELECT cantidad FROM inventario WHERE producto_id=%s", (pid,))
        ant = c.fetchone()
        if not ant: warn("Producto no encontrado"); c.close(); pausar(); return
        c.execute("UPDATE inventario SET cantidad=%s WHERE producto_id=%s", (int(cantidad), pid))
        PG_CONN.commit()
        ok(f"Stock actualizado: {ant['cantidad']} → [bold cyan]{cantidad}[/bold cyan]")

        if MONGO_DB is not None:
            c2 = cur()
            c2.execute("SELECT nombre FROM producto WHERE id=%s", (pid,))
            prod = c2.fetchone()
            c2.close()
            MONGO_DB.eventos_historial.insert_one({
                "tipo": "ajuste_inventario",
                "fecha": datetime.datetime.now(),
                "descripcion": f"Ajuste manual stock {prod['nombre'] if prod else 'prod '+pid}: {ant['cantidad']} → {cantidad}",
                "producto_id": int(pid),
                "usuario_id": 1,
                "metadata": {"cantidad_anterior": ant["cantidad"], "cantidad_nueva": int(cantidad),
                             "motivo": "Ajuste manual desde demo"}
            })
            ok("Evento de ajuste registrado en MongoDB 🍃")
        c.close()
    except Exception as e:
        PG_CONN.rollback(); err(f"Error: {e}")
    pausar()

def pg_cambiar_estado_venta():
    section("Cambiar Estado de Venta", "yellow", "💳")
    pg_ver_ventas()
    vid    = Prompt.ask("  ID de la venta")
    estado = Prompt.ask("  Nuevo estado", choices=["pendiente","completada","cancelada"])
    try:
        c = cur()
        c.execute("UPDATE venta SET estado=%s WHERE id=%s", (estado, vid))
        PG_CONN.commit()
        ok(f"Venta #{vid} → estado [bold cyan]{estado}[/bold cyan]")
        c.close()
    except Exception as e:
        PG_CONN.rollback(); err(f"Error: {e}")
    pausar()

def pg_cambiar_precio():
    section("Cambiar Precio de Producto", "yellow", "💲")
    pg_ver_productos()
    pid    = Prompt.ask("  ID del producto")
    precio = Prompt.ask("  Nuevo precio (COP)")
    try:
        c = cur()
        c.execute("UPDATE producto SET precio=%s WHERE id=%s", (float(precio), pid))
        PG_CONN.commit()
        ok(f"Precio del producto #{pid} actualizado a [bold green]${float(precio):,.0f}[/bold green]")
        c.close()
    except Exception as e:
        PG_CONN.rollback(); err(f"Error: {e}")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  POSTGRESQL — ELIMINAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_pg_eliminar():
    if not PG_CONN: err("Sin conexión a PostgreSQL"); return
    while True:
        section("PostgreSQL — Eliminar", "red", "🗑")
        console.print("  [red]1[/red] Eliminar cliente")
        console.print("  [red]2[/red] Eliminar venta")
        console.print("  [red]3[/red] Eliminar producto")
        console.print("  [red]0[/red] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": pg_eliminar_cliente()
        elif op == "2": pg_eliminar_venta()
        elif op == "3": pg_eliminar_producto()
        elif op == "0": break
        else: warn("Opción no válida")

def pg_eliminar_cliente():
    section("Eliminar Cliente", "red", "🗑")
    pg_ver_clientes()
    cid = Prompt.ask("  ID del cliente a eliminar")
    if not Confirm.ask(f"  ¿Confirmar eliminación del cliente #{cid}?"): return
    try:
        c = cur()
        c.execute("DELETE FROM cliente WHERE id=%s", (cid,))
        PG_CONN.commit()
        ok(f"Cliente #{cid} eliminado")
        c.close()
    except Exception as e:
        PG_CONN.rollback()
        err(f"Error: {e}")
        warn("Puede tener ventas asociadas — elimínalas primero")
    pausar()

def pg_eliminar_venta():
    section("Eliminar Venta", "red", "🗑")
    pg_ver_ventas()
    vid = Prompt.ask("  ID de la venta a eliminar")
    if not Confirm.ask(f"  ¿Confirmar eliminación de la venta #{vid}? (También elimina el detalle)"): return
    try:
        c = cur()
        c.execute("DELETE FROM venta WHERE id=%s", (vid,))
        PG_CONN.commit()
        ok(f"Venta #{vid} y su detalle eliminados (CASCADE)")
        c.close()
    except Exception as e:
        PG_CONN.rollback(); err(f"Error: {e}")
    pausar()

def pg_eliminar_producto():
    section("Eliminar Producto", "red", "🗑")
    pg_ver_productos()
    pid = Prompt.ask("  ID del producto a eliminar")
    if not Confirm.ask(f"  ¿Confirmar eliminación del producto #{pid}?"): return
    try:
        c = cur()
        c.execute("DELETE FROM producto WHERE id=%s", (pid,))
        PG_CONN.commit()
        ok(f"Producto #{pid} eliminado")
        c.close()
    except Exception as e:
        PG_CONN.rollback()
        err(f"Error: {e}")
        warn("Puede tener ventas asociadas — no se puede eliminar (RESTRICT)")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DEMO TRIGGER ACID
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def demo_trigger():
    if not PG_CONN: err("Sin conexión a PostgreSQL"); return
    section("DEMO TRIGGER ACID — Atomicidad del Stock", "bright_yellow", "⚡")

    code = Syntax("""\
-- trg_descontar_stock se dispara AFTER INSERT en detalle_venta
-- 1. Verifica stock disponible
-- 2. Descuenta la cantidad  (atómico con la inserción)
-- 3. Si stock < cantidad → RAISE EXCEPTION → ROLLBACK automático

INSERT INTO detalle_venta(venta_id, producto_id, cantidad, precio_unitario)
VALUES (1, 1, 999999, 12500);
-- → ERROR esperado: Stock insuficiente
""", "sql", theme="one-dark")
    console.print(Padding(Panel(code, title="[bold yellow]SQL a ejecutar[/bold yellow]",
                                border_style="yellow"), (0,4)))

    c = cur()
    c.execute("SELECT cantidad FROM inventario WHERE producto_id=1")
    row = c.fetchone()
    stock_antes = row["cantidad"] if row else "?"
    info(f"Stock del producto 1 ANTES: [bold cyan]{stock_antes}[/bold cyan]")
    console.print()

    try:
        c.execute("INSERT INTO detalle_venta(venta_id, producto_id, cantidad, precio_unitario) VALUES (1,1,999999,12500)")
        PG_CONN.commit()
        warn("El trigger no se disparó")
    except Exception as e:
        PG_CONN.rollback()
        ok("[bold green]Trigger disparado — transacción revertida (ROLLBACK)[/bold green]")
        console.print(Panel(f"  [red]{e}[/red]",
                            title="[bold red]Error capturado (esperado)[/bold red]",
                            border_style="red", padding=(0,2)))

    c2 = cur()
    c2.execute("SELECT cantidad FROM inventario WHERE producto_id=1")
    row2 = c2.fetchone()
    stock_despues = row2["cantidad"] if row2 else "?"
    console.print()
    ok(f"Stock DESPUÉS: [bold cyan]{stock_despues}[/bold cyan] — sin cambios, integridad preservada ✔")
    c.close(); c2.close()
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MONGODB — CONSULTAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_mongo_consultas():
    if not MONGO_DB: err("Sin conexión a MongoDB"); return
    while True:
        section("MongoDB — Consultas", "green", "🍃")
        console.print("  [green]1[/green] Todos los lotes de producción")
        console.print("  [green]2[/green] Lotes por producto ID")
        console.print("  [green]3[/green] Historial de eventos")
        console.print("  [green]4[/green] Solo alertas de stock")
        console.print("  [green]5[/green] Agregación: total producido por producto")
        console.print("  [green]0[/green] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": mongo_ver_lotes()
        elif op == "2": mongo_lotes_por_producto()
        elif op == "3": mongo_ver_eventos()
        elif op == "4": mongo_alertas()
        elif op == "5": mongo_agregacion()
        elif op == "0": break
        else: warn("Opción no válida")

def mongo_ver_lotes():
    section("Lotes de Producción", "green", "🏭")
    docs = list(MONGO_DB.lotes_produccion.find({}, {"_id":0}).sort("fecha",-1))
    _render_lotes(docs)
    pausar()

def mongo_lotes_por_producto():
    section("Lotes por Producto", "green", "🏭")
    pid = Prompt.ask("  ID del producto (referencia PostgreSQL)")
    docs = list(MONGO_DB.lotes_produccion.find(
        {"producto_id": int(pid)}, {"_id":0}).sort("fecha",-1))
    if not docs:
        warn(f"No hay lotes para el producto {pid}")
    else:
        _render_lotes(docs)
    pausar()

def mongo_ver_eventos():
    section("Historial de Eventos", "green", "📋")
    docs = list(MONGO_DB.eventos_historial.find({}, {"_id":0}).sort("fecha",-1).limit(10))
    _render_eventos(docs)
    pausar()

def mongo_alertas():
    section("Alertas de Stock", "red", "🚨")
    docs = list(MONGO_DB.eventos_historial.find(
        {"tipo":"alerta_stock"}, {"_id":0}).sort("fecha",-1))
    if not docs:
        ok("Sin alertas registradas en MongoDB")
    else:
        _render_eventos(docs)
    pausar()

def mongo_agregacion():
    section("Agregación — Total Producido por Producto", "green", "📊")
    pipeline = [
        {"$group": {"_id":"$producto_id",
                    "total_kg":{"$sum":"$cantidad_producida"},
                    "lotes":{"$sum":1},
                    "ultima":{"$max":"$fecha"}}},
        {"$sort":{"total_kg":-1}}
    ]
    docs = list(MONGO_DB.lotes_produccion.aggregate(pipeline))
    t = Table(box=box.HEAVY_HEAD, border_style="green", header_style="bold white on dark_green")
    t.add_column("Producto ID", justify="center", style="cyan")
    t.add_column("Total (kg)",  justify="right",  style="bold white")
    t.add_column("Lotes",       justify="center",  style="bold yellow")
    t.add_column("Visual", width=22)
    mx = max((d["total_kg"] for d in docs), default=1)
    for d in docs:
        bar = Text("█"*int(d["total_kg"]/mx*20) + "░"*(20-int(d["total_kg"]/mx*20)), style="green")
        t.add_row(str(d["_id"]), str(d["total_kg"]), str(d["lotes"]), bar)
    console.print(Padding(t, (0,4)))
    pausar()

def _render_lotes(docs):
    t = Table(box=box.ROUNDED, border_style="green", header_style="bold white on dark_green", show_lines=True)
    t.add_column("Prod.ID", justify="center", style="cyan", width=8)
    t.add_column("Fecha",   style="bright_black")
    t.add_column("Cant.",   justify="right", style="bold white")
    t.add_column("Calidad", justify="center")
    t.add_column("Origen",  style="dim")
    CAL = {"alta":"bold green","media":"bold yellow","baja":"bold red"}
    for d in docs:
        cal = str(d.get("calidad","—"))
        t.add_row(str(d.get("producto_id","—")),
                  str(d.get("fecha","—"))[:10],
                  str(d.get("cantidad_producida","—")),
                  Text(cal, style=CAL.get(cal,"white")),
                  str(d.get("origen","—")))
    console.print(Padding(t, (0,4)))

def _render_eventos(docs):
    t = Table(box=box.SIMPLE_HEAD, border_style="bright_black",
              header_style="bold bright_white", show_lines=False)
    t.add_column("Tipo",        justify="center", width=22)
    t.add_column("Fecha",       style="bright_black", width=18)
    t.add_column("Descripción")
    for d in docs:
        tipo  = str(d.get("tipo","—"))
        color = TIPO_COLOR.get(tipo,"white")
        t.add_row(Text(f" {tipo} ", style=f"bold white on {color}"),
                  str(d.get("fecha","—"))[:16],
                  str(d.get("descripcion","—")))
    console.print(Padding(t, (0,4)))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MONGODB — INSERTAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_mongo_insertar():
    if not MONGO_DB: err("Sin conexión a MongoDB"); return
    while True:
        section("MongoDB — Insertar", "green", "➕")
        console.print("  [green]1[/green] Nuevo lote de producción")
        console.print("  [green]2[/green] Nuevo evento manual")
        console.print("  [green]0[/green] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": mongo_insertar_lote()
        elif op == "2": mongo_insertar_evento()
        elif op == "0": break
        else: warn("Opción no válida")

def mongo_insertar_lote():
    section("Nuevo Lote de Producción", "green", "🏭")
    pid      = Prompt.ask("  ID del producto (ref. PostgreSQL)")
    cantidad = Prompt.ask("  Cantidad producida (kg/unidades)")
    calidad  = Prompt.ask("  Calidad", choices=["alta","media","baja"])
    origen   = Prompt.ask("  Origen (vereda, finca, asociación)")
    notas    = Prompt.ask("  Notas (opcional)", default="")

    doc = {
        "producto_id": int(pid),
        "usuario_id": 1,
        "fecha": datetime.datetime.now(),
        "cantidad_producida": int(cantidad),
        "calidad": calidad,
        "origen": origen,
        "notas": notas,
        "datos_variables": {}
    }

    console.print()
    info("¿Deseas agregar atributos extra en [bold]datos_variables[/bold]? (temperatura, variedad, etc.)")
    if Confirm.ask("  Agregar atributos extra"):
        while True:
            clave = Prompt.ask("  Nombre del atributo (Enter para terminar)", default="")
            if not clave: break
            valor = Prompt.ask(f"  Valor de '{clave}'")
            doc["datos_variables"][clave] = valor

    result = MONGO_DB.lotes_produccion.insert_one(doc)
    ok(f"Lote insertado con ID [cyan]{result.inserted_id}[/cyan]")

    MONGO_DB.eventos_historial.insert_one({
        "tipo": "produccion",
        "fecha": datetime.datetime.now(),
        "descripcion": f"Lote {cantidad} kg/u registrado — {origen}",
        "producto_id": int(pid),
        "usuario_id": 1,
        "metadata": {"cantidad": int(cantidad), "calidad": calidad, "origen": origen}
    })
    ok("Evento de producción registrado en eventos_historial ✔")
    pausar()

def mongo_insertar_evento():
    section("Nuevo Evento Manual", "green", "📋")
    tipo = Prompt.ask("  Tipo", choices=["produccion","venta","ajuste_inventario","devolucion","alerta_stock"])
    desc = Prompt.ask("  Descripción")
    pid  = Prompt.ask("  ID del producto (opcional)", default="")
    doc = {
        "tipo": tipo,
        "fecha": datetime.datetime.now(),
        "descripcion": desc,
        "usuario_id": 1,
        "metadata": {}
    }
    if pid:
        doc["producto_id"] = int(pid)
    result = MONGO_DB.eventos_historial.insert_one(doc)
    ok(f"Evento insertado con ID [cyan]{result.inserted_id}[/cyan]")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MONGODB — ELIMINAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def menu_mongo_eliminar():
    if not MONGO_DB: err("Sin conexión a MongoDB"); return
    while True:
        section("MongoDB — Eliminar", "red", "🗑")
        console.print("  [red]1[/red] Eliminar lotes de un producto")
        console.print("  [red]2[/red] Eliminar eventos de un tipo")
        console.print("  [red]3[/red] Eliminar último documento insertado")
        console.print("  [red]0[/red] Volver")
        console.print()
        op = Prompt.ask("  Opción").strip()
        if   op == "1": mongo_eliminar_lotes()
        elif op == "2": mongo_eliminar_eventos_tipo()
        elif op == "3": mongo_eliminar_ultimo()
        elif op == "0": break
        else: warn("Opción no válida")

def mongo_eliminar_lotes():
    section("Eliminar Lotes por Producto", "red", "🗑")
    pid = Prompt.ask("  ID del producto cuyos lotes eliminar")
    total = MONGO_DB.lotes_produccion.count_documents({"producto_id": int(pid)})
    if total == 0:
        warn(f"No hay lotes para el producto {pid}"); pausar(); return
    if not Confirm.ask(f"  ¿Eliminar los {total} lotes del producto #{pid}?"): return
    res = MONGO_DB.lotes_produccion.delete_many({"producto_id": int(pid)})
    ok(f"{res.deleted_count} lotes eliminados")
    pausar()

def mongo_eliminar_eventos_tipo():
    section("Eliminar Eventos por Tipo", "red", "🗑")
    tipo = Prompt.ask("  Tipo a eliminar", choices=["produccion","venta","ajuste_inventario","devolucion","alerta_stock"])
    total = MONGO_DB.eventos_historial.count_documents({"tipo": tipo})
    if total == 0:
        warn(f"No hay eventos de tipo '{tipo}'"); pausar(); return
    if not Confirm.ask(f"  ¿Eliminar los {total} eventos de tipo '{tipo}'?"): return
    res = MONGO_DB.eventos_historial.delete_many({"tipo": tipo})
    ok(f"{res.deleted_count} eventos eliminados")
    pausar()

def mongo_eliminar_ultimo():
    section("Eliminar Último Documento", "red", "🗑")
    col = Prompt.ask("  Colección", choices=["lotes_produccion","eventos_historial"])
    doc = MONGO_DB[col].find_one({}, sort=[("_id",-1)])
    if not doc:
        warn("Colección vacía"); pausar(); return
    console.print(Panel(
        f"  [dim]Tipo:[/dim] {doc.get('tipo', doc.get('calidad','—'))}\n"
        f"  [dim]Desc:[/dim] {doc.get('descripcion', doc.get('origen','—'))}\n"
        f"  [dim]Fecha:[/dim] {str(doc.get('fecha','—'))[:16]}",
        title="[bold red]Documento a eliminar[/bold red]", border_style="red"))
    if not Confirm.ask("  ¿Confirmar eliminación?"): return
    MONGO_DB[col].delete_one({"_id": doc["_id"]})
    ok("Documento eliminado")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RESUMEN ARQUITECTÓNICO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def resumen_arquitectura():
    section("Resumen de Arquitectura Políglota", "bright_magenta", "🏛")
    pg = Panel(
        "\n".join([
            "[bold cyan]Motor:[/bold cyan] PostgreSQL · ACID · CP",
            "", "[bold white]Entidades:[/bold white]",
            "  • usuario      • cliente",
            "  • producto     • inventario",
            "  • venta        • detalle_venta",
            "", "[bold white]Triggers:[/bold white]",
            "  ⚡ trg_descontar_stock",
            "  ⚡ trg_recalcular_total",
            "  ⚡ trg_alerta_stock",
            "  ⚡ trg_inventario_updated",
        ]),
        title="[bold cyan]🐘 Capa Relacional[/bold cyan]",
        border_style="cyan", padding=(1,2)
    )
    mongo = Panel(
        "\n".join([
            "[bold green]Motor:[/bold green] MongoDB · BASE · AP",
            "", "[bold white]Colecciones:[/bold white]",
            "  • lotes_produccion",
            "  • eventos_historial",
            "", "[bold white]Características:[/bold white]",
            "  📄 Esquema flexible (datos_variables)",
            "  📈 Alta velocidad de escritura",
            "  🔗 Referencia por producto_id → PG",
        ]),
        title="[bold green]🍃 Capa Documental[/bold green]",
        border_style="green", padding=(1,2)
    )
    from rich.columns import Columns
    console.print(Padding(Columns([pg, mongo]), (0,2)))

    t = Table(title="⚖  Trade-offs", box=box.ROUNDED,
              border_style="bright_magenta", header_style="bold white on dark_magenta", show_lines=True)
    t.add_column("Aspecto",    style="bold white",  width=18)
    t.add_column("PostgreSQL", justify="center", style="cyan")
    t.add_column("MongoDB",    justify="center", style="green")
    for row in [
        ("Consistencia",  "Fuerte (inmediata)",        "Eventual (ms)"),
        ("Esquema",       "Rígido (migraciones)",      "Flexible"),
        ("Transacciones", "Nativas distribuidas",      "Lógica en app"),
        ("Escalabilidad", "Vertical",                  "Horizontal"),
        ("Caso de uso",   "Ventas / inventario",       "Logs / lotes"),
    ]:
        t.add_row(*row)
    console.print(Padding(t, (0,4)))
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  GENERAR HTML
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generar_html():
    section("Generando Dashboard HTML", "bright_cyan", "🌐")

    # recolectar datos
    productos, ventas, lotes, eventos = [], [], [], []
    if PG_CONN:
        c = cur()
        c.execute("SELECT p.id, p.nombre, p.precio, i.cantidad AS stock, i.cantidad_minima AS minimo FROM producto p JOIN inventario i ON i.producto_id=p.id ORDER BY p.id")
        productos = [dict(r) for r in c.fetchall()]
        c.execute("SELECT v.id, cl.nombre AS cliente, v.fecha::date AS fecha, v.total, v.estado FROM venta v JOIN cliente cl ON cl.id=v.cliente_id ORDER BY v.fecha DESC LIMIT 10")
        ventas = [{**dict(r), "fecha": str(r["fecha"]), "total": float(r["total"])} for r in c.fetchall()]
        c.close()
    if MONGO_DB is not None:
        lotes   = [{**d, "_id": str(d["_id"]), "fecha": str(d.get("fecha",""))[:10]} for d in MONGO_DB.lotes_produccion.find().sort("fecha",-1)]
        eventos = [{**d, "_id": str(d["_id"]), "fecha": str(d.get("fecha",""))[:16]} for d in MONGO_DB.eventos_historial.find().sort("fecha",-1).limit(10)]

    def filas_productos():
        rows = []
        for p in productos:
            alrt = "⚠" if p["stock"] <= p["minimo"] else ""
            cls  = "alert" if p["stock"] <= p["minimo"] else ""
            rows.append(f'<tr class="{cls}"><td>{p["id"]}</td><td>{p["nombre"]}</td><td>${float(p["precio"]):,.0f}</td><td>{p["stock"]} {alrt}</td><td>{p["minimo"]}</td></tr>')
        return "".join(rows)

    def filas_ventas():
        EC = {"completada":"badge-green","pendiente":"badge-yellow","cancelada":"badge-red"}
        return "".join(f'<tr><td>#{v["id"]}</td><td>{v["cliente"]}</td><td>{v["fecha"]}</td><td>${float(v["total"]):,.0f}</td><td><span class="badge {EC.get(v["estado"],"")}">{v["estado"]}</span></td></tr>' for v in ventas)

    def filas_lotes():
        CC = {"alta":"badge-green","media":"badge-yellow","baja":"badge-red"}
        return "".join(f'<tr><td>{l.get("producto_id","—")}</td><td>{l.get("fecha","—")}</td><td>{l.get("cantidad_producida","—")}</td><td><span class="badge {CC.get(str(l.get("calidad","")),"")}">{l.get("calidad","—")}</span></td><td>{l.get("origen","—")}</td></tr>' for l in lotes)

    def tarjetas_eventos():
        TI = {"produccion":("🏭","#22c55e"),"venta":("💳","#3b82f6"),"ajuste_inventario":("🔧","#f59e0b"),"devolucion":("↩️","#a855f7"),"alerta_stock":("🚨","#ef4444")}
        cards = []
        for e in eventos:
            icon, color = TI.get(e.get("tipo",""), ("📄","#6b7280"))
            cards.append(f'<div class="event-card" style="border-left:4px solid {color}"><span class="event-icon">{icon}</span><div><div class="event-tipo" style="color:{color}">{e.get("tipo","—").replace("_"," ").upper()}</div><div class="event-desc">{e.get("descripcion","—")}</div><div class="event-fecha">{e.get("fecha","—")}</div></div></div>')
        return "".join(cards)

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Demo — Persistencia Políglota · Inventario Rural</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--pg:#22d3ee;--mongo:#4ade80;--bg:#050b14;--card:#0f2236;--border:#1a3a55;--text:#e2f0ff;--muted:#607d9a;--accent:#f0a500}}
body{{background:var(--bg);color:var(--text);font-family:'Syne',sans-serif;background-image:radial-gradient(ellipse 80% 60% at 10% 0%,rgba(34,211,238,.07) 0%,transparent 60%),radial-gradient(ellipse 60% 50% at 90% 100%,rgba(74,222,128,.06) 0%,transparent 60%)}}
header{{padding:3rem 4rem 2rem;border-bottom:1px solid var(--border);display:flex;align-items:flex-end;justify-content:space-between;flex-wrap:wrap;gap:1rem}}
h1{{font-size:clamp(1.8rem,4vw,2.8rem);font-weight:800;background:linear-gradient(90deg,var(--pg),var(--mongo));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
header p{{font-family:'Space Mono',monospace;color:var(--muted);font-size:.8rem;margin-top:.4rem}}
.badges{{display:flex;gap:.6rem;flex-wrap:wrap}}
.hbadge{{font-family:'Space Mono',monospace;font-size:.7rem;padding:.35rem .8rem;border-radius:4px;font-weight:700;text-transform:uppercase}}
.hbadge.pg{{background:rgba(34,211,238,.12);color:var(--pg);border:1px solid rgba(34,211,238,.25)}}
.hbadge.mongo{{background:rgba(74,222,128,.12);color:var(--mongo);border:1px solid rgba(74,222,128,.25)}}
.hbadge.date{{background:rgba(240,165,0,.1);color:var(--accent);border:1px solid rgba(240,165,0,.2)}}
main{{padding:2.5rem 4rem;display:grid;gap:2rem}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:2rem}}
@media(max-width:900px){{main{{padding:1.5rem}}.grid-2{{grid-template-columns:1fr}}}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;position:relative;animation:fadeUp .5s ease both}}
.card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--pg),var(--mongo))}}
.card.pg::before{{background:var(--pg)}}.card.mongo::before{{background:var(--mongo)}}
.card-header{{padding:1.2rem 1.5rem .8rem;display:flex;align-items:center;gap:.7rem;border-bottom:1px solid var(--border)}}
.card-header h2{{font-size:1rem;font-weight:700}}
.layer-badge{{font-family:'Space Mono',monospace;font-size:.65rem;padding:.2rem .5rem;border-radius:3px;font-weight:700;text-transform:uppercase;margin-left:auto}}
.layer-badge.pg{{background:rgba(34,211,238,.15);color:var(--pg);border:1px solid rgba(34,211,238,.3)}}
.layer-badge.mongo{{background:rgba(74,222,128,.15);color:var(--mongo);border:1px solid rgba(74,222,128,.3)}}
.table-wrap{{overflow-x:auto}}
table{{width:100%;border-collapse:collapse;font-size:.85rem}}
th{{text-align:left;padding:.7rem 1.2rem;font-family:'Space Mono',monospace;font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);background:rgba(255,255,255,.02);border-bottom:1px solid var(--border)}}
td{{padding:.7rem 1.2rem;border-bottom:1px solid rgba(26,58,85,.5)}}
tr:last-child td{{border-bottom:none}}
tr:hover td{{background:rgba(255,255,255,.02)}}
tr.alert td{{color:#fca5a5;background:rgba(239,68,68,.04)}}
.badge{{font-family:'Space Mono',monospace;font-size:.68rem;padding:.2rem .55rem;border-radius:3px;font-weight:700;text-transform:uppercase}}
.badge-green{{background:rgba(74,222,128,.15);color:#4ade80;border:1px solid rgba(74,222,128,.3)}}
.badge-yellow{{background:rgba(250,204,21,.12);color:#facc15;border:1px solid rgba(250,204,21,.3)}}
.badge-red{{background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.3)}}
.trigger-box{{background:#020c14;border:1px solid var(--border);border-radius:12px;overflow:hidden}}
.trigger-header{{padding:1rem 1.5rem;background:rgba(240,165,0,.07);border-bottom:1px solid rgba(240,165,0,.2);font-family:'Space Mono',monospace;font-size:.8rem;color:var(--accent)}}
pre.sql-code{{font-family:'Space Mono',monospace;font-size:.78rem;line-height:1.7;padding:1.5rem;color:#a5d6ff;overflow-x:auto}}
pre.sql-code .kw{{color:#f0a500;font-weight:700}}
pre.sql-code .cmt{{color:#4b6a88;font-style:italic}}
.result-ok{{margin:0 1.5rem 1.5rem;padding:1rem;background:rgba(74,222,128,.06);border:1px solid rgba(74,222,128,.2);border-radius:8px;font-family:'Space Mono',monospace;font-size:.8rem;color:#4ade80}}
.result-err{{margin:0 1.5rem 1rem;padding:1rem;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.2);border-radius:8px;font-family:'Space Mono',monospace;font-size:.75rem;color:#f87171;line-height:1.6}}
.events-list{{padding:.8rem 1.2rem 1.2rem;display:flex;flex-direction:column;gap:.6rem}}
.event-card{{display:flex;align-items:flex-start;gap:.9rem;padding:.8rem 1rem;background:rgba(255,255,255,.025);border-radius:8px}}
.event-icon{{font-size:1.2rem;flex-shrink:0;margin-top:.1rem}}
.event-tipo{{font-family:'Space Mono',monospace;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em}}
.event-desc{{font-size:.85rem;color:var(--text);margin-top:.15rem}}
.event-fecha{{font-family:'Space Mono',monospace;font-size:.7rem;color:var(--muted);margin-top:.2rem}}
footer{{text-align:center;padding:2rem;border-top:1px solid var(--border);font-family:'Space Mono',monospace;font-size:.75rem;color:var(--muted)}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
</head>
<body>
<header>
  <div><h1>Persistencia Políglota</h1><p>// Sistema de Inventario Rural · Bases de Datos II · Grupo 10</p></div>
  <div class="badges">
    <span class="hbadge pg">🐘 PostgreSQL · ACID</span>
    <span class="hbadge mongo">🍃 MongoDB · BASE</span>
    <span class="hbadge date">📅 {now}</span>
  </div>
</header>
<main>
  <div class="grid-2">
    <div class="card pg">
      <div class="card-header"><span>📦</span><h2>Productos e Inventario</h2><span class="layer-badge pg">PostgreSQL</span></div>
      <div class="table-wrap"><table><thead><tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Mín.</th></tr></thead><tbody>{filas_productos()}</tbody></table></div>
    </div>
    <div class="card pg">
      <div class="card-header"><span>💳</span><h2>Ventas Recientes</h2><span class="layer-badge pg">PostgreSQL</span></div>
      <div class="table-wrap"><table><thead><tr><th>#</th><th>Cliente</th><th>Fecha</th><th>Total</th><th>Estado</th></tr></thead><tbody>{filas_ventas()}</tbody></table></div>
    </div>
  </div>
  <div class="trigger-box">
    <div class="trigger-header">⚡  DEMO TRIGGER ACID — trg_descontar_stock · Atomicidad garantizada</div>
    <pre class="sql-code"><span class="cmt">-- El trigger verifica stock antes de descontar.</span>
<span class="cmt">-- Si stock &lt; cantidad → ROLLBACK automático (Atomicidad ACID).</span>

<span class="kw">INSERT INTO</span> detalle_venta(venta_id, producto_id, cantidad, precio_unitario)
<span class="kw">VALUES</span> (1, 1, 999999, 12500);</pre>
    <div class="result-err">✘  ERROR: Stock insuficiente — pedido=999999 &gt; stock disponible<br>&nbsp;&nbsp;&nbsp;→ Transacción revertida por completo (ROLLBACK)</div>
    <div class="result-ok">✔  Stock sin cambios — Integridad preservada (Atomicidad ACID) ✔</div>
  </div>
  <div class="grid-2">
    <div class="card mongo">
      <div class="card-header"><span>🏭</span><h2>Lotes de Producción</h2><span class="layer-badge mongo">MongoDB</span></div>
      <div class="table-wrap"><table><thead><tr><th>Prod.ID</th><th>Fecha</th><th>Cantidad</th><th>Calidad</th><th>Origen</th></tr></thead><tbody>{filas_lotes()}</tbody></table></div>
    </div>
    <div class="card mongo">
      <div class="card-header"><span>📋</span><h2>Historial de Eventos</h2><span class="layer-badge mongo">MongoDB</span></div>
      <div class="events-list">{tarjetas_eventos()}</div>
    </div>
  </div>
</main>
<footer>Generado por <span style="color:var(--text)">demo_poliglota.py</span> · Grupo 10: <span style="color:var(--text)">Santiago Chavarro & Juan Pablo Sánchez</span> · {now}</footer>
</body></html>"""

    out = Path.home() / "Downloads" / "demo_results.html"
    out.write_text(html, encoding="utf-8")
    ok(f"Dashboard generado → [bold cyan]{out}[/bold cyan]")
    info("Ábrelo en el navegador con doble clic")
    pausar()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    splash()
    conectar()
    menu_principal()

if __name__ == "__main__":
    main()
