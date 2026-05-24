--
-- PostgreSQL database dump
--

\restrict w0AhKHIGjPJ2iOHsG9euHqBAyRsxedAnyUSrTqGKtukPhIFSVUawDQGTcgLgEfJ

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

-- Started on 2026-05-24 17:25:50

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 234 (class 1255 OID 41509)
-- Name: fn_alerta_stock(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_alerta_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.cantidad <= NEW.cantidad_minima THEN
        RAISE NOTICE 'ALERTA STOCK BAJO - Producto id=%, actual=%, minimo=%',
            NEW.producto_id, NEW.cantidad, NEW.cantidad_minima;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_alerta_stock() OWNER TO postgres;

--
-- TOC entry 232 (class 1255 OID 41505)
-- Name: fn_descontar_stock(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_descontar_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    stock_actual INT;
BEGIN
    SELECT cantidad INTO stock_actual
    FROM inventario
    WHERE producto_id = NEW.producto_id;

    IF stock_actual < NEW.cantidad THEN
        RAISE EXCEPTION 'Stock insuficiente. Producto id=%, stock actual=%, pedido=%',
            NEW.producto_id, stock_actual, NEW.cantidad;
    END IF;

    UPDATE inventario
    SET cantidad = cantidad - NEW.cantidad
    WHERE producto_id = NEW.producto_id;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_descontar_stock() OWNER TO postgres;

--
-- TOC entry 231 (class 1255 OID 41503)
-- Name: fn_inventario_updated(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_inventario_updated() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_inventario_updated() OWNER TO postgres;

--
-- TOC entry 233 (class 1255 OID 41507)
-- Name: fn_recalcular_total(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_recalcular_total() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE v_id INT;
BEGIN
    v_id := COALESCE(NEW.venta_id, OLD.venta_id);
    UPDATE venta
    SET total = (
        SELECT COALESCE(SUM(cantidad * precio_unitario), 0)
        FROM detalle_venta WHERE venta_id = v_id
    )
    WHERE id = v_id;
    RETURN COALESCE(NEW, OLD);
END;
$$;


ALTER FUNCTION public.fn_recalcular_total() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 41412)
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    email character varying(150),
    telefono character varying(20),
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 41411)
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO postgres;

--
-- TOC entry 5092 (class 0 OID 0)
-- Dependencies: 221
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- TOC entry 230 (class 1259 OID 41481)
-- Name: detalle_venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_venta (
    id integer NOT NULL,
    venta_id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    CONSTRAINT detalle_venta_cantidad_check CHECK ((cantidad > 0))
);


ALTER TABLE public.detalle_venta OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 41480)
-- Name: detalle_venta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_venta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_venta_id_seq OWNER TO postgres;

--
-- TOC entry 5093 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_venta_id_seq OWNED BY public.detalle_venta.id;


--
-- TOC entry 226 (class 1259 OID 41442)
-- Name: inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventario (
    id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer DEFAULT 0 NOT NULL,
    cantidad_minima integer DEFAULT 5 NOT NULL,
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.inventario OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 41441)
-- Name: inventario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventario_id_seq OWNER TO postgres;

--
-- TOC entry 5094 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventario_id_seq OWNED BY public.inventario.id;


--
-- TOC entry 224 (class 1259 OID 41422)
-- Name: producto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text,
    precio numeric(10,2) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT producto_precio_check CHECK ((precio >= (0)::numeric))
);


ALTER TABLE public.producto OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 41421)
-- Name: producto_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.producto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.producto_id_seq OWNER TO postgres;

--
-- TOC entry 5095 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producto_id_seq OWNED BY public.producto.id;


--
-- TOC entry 220 (class 1259 OID 41396)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer NOT NULL,
    nombre character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password character varying(255) NOT NULL,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 41395)
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- TOC entry 5096 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- TOC entry 228 (class 1259 OID 41463)
-- Name: venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.venta (
    id integer NOT NULL,
    cliente_id integer NOT NULL,
    fecha timestamp without time zone DEFAULT now(),
    total numeric(12,2) DEFAULT 0,
    estado character varying(20) DEFAULT 'pendiente'::character varying,
    CONSTRAINT venta_estado_check CHECK (((estado)::text = ANY ((ARRAY['pendiente'::character varying, 'completada'::character varying, 'cancelada'::character varying])::text[])))
);


ALTER TABLE public.venta OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 41462)
-- Name: venta_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.venta_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.venta_id_seq OWNER TO postgres;

--
-- TOC entry 5097 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.venta_id_seq OWNED BY public.venta.id;


--
-- TOC entry 4887 (class 2604 OID 41415)
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- TOC entry 4899 (class 2604 OID 41484)
-- Name: detalle_venta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta ALTER COLUMN id SET DEFAULT nextval('public.detalle_venta_id_seq'::regclass);


--
-- TOC entry 4891 (class 2604 OID 41445)
-- Name: inventario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario ALTER COLUMN id SET DEFAULT nextval('public.inventario_id_seq'::regclass);


--
-- TOC entry 4889 (class 2604 OID 41425)
-- Name: producto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto ALTER COLUMN id SET DEFAULT nextval('public.producto_id_seq'::regclass);


--
-- TOC entry 4885 (class 2604 OID 41399)
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- TOC entry 4895 (class 2604 OID 41466)
-- Name: venta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta ALTER COLUMN id SET DEFAULT nextval('public.venta_id_seq'::regclass);


--
-- TOC entry 5078 (class 0 OID 41412)
-- Dependencies: 222
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cliente (id, nombre, email, telefono, created_at) FROM stdin;
1	Cooperativa Huila Verde	contacto@huilaverde.co	3101234567	2026-05-24 12:51:59.605526
2	Distribuidora El Macizo	ventas@elmacizo.co	3157654321	2026-05-24 12:51:59.605526
3	Tienda Rural La Cosecha	lacosecha@gmail.com	3124569870	2026-05-24 12:51:59.605526
\.


--
-- TOC entry 5086 (class 0 OID 41481)
-- Dependencies: 230
-- Data for Name: detalle_venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_venta (id, venta_id, producto_id, cantidad, precio_unitario) FROM stdin;
1	1	1	480	12500.00
2	2	2	10	28000.00
3	2	3	30	3800.00
4	3	3	30	3800.00
5	3	4	6	18500.00
\.


--
-- TOC entry 5082 (class 0 OID 41442)
-- Dependencies: 226
-- Data for Name: inventario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventario (id, producto_id, cantidad, cantidad_minima, updated_at) FROM stdin;
5	5	160	60	2026-05-24 12:51:59.605526
2	2	28	50	2026-05-24 12:51:59.605526
3	3	150	80	2026-05-24 12:51:59.605526
4	4	6	20	2026-05-24 12:51:59.605526
1	1	480	100	2026-05-24 12:53:52.076316
6	6	45	2	2026-05-24 15:58:33.154656
7	7	34	3	2026-05-24 16:03:06.830539
\.


--
-- TOC entry 5080 (class 0 OID 41422)
-- Dependencies: 224
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto (id, usuario_id, nombre, descripcion, precio, created_at) FROM stdin;
1	1	Café Pergamino Húmedo	Café en pergamino cosecha propia, secado en marquesina	12500.00	2026-05-24 12:51:59.605526
2	1	Café Tostado Molido	Café tostado medio, molido fino, empacado al vacío 500g	28000.00	2026-05-24 12:51:59.605526
3	1	Panela en Bloque	Panela artesanal sin aditivos, producción trapiche San Marcos	3800.00	2026-05-24 12:51:59.605526
4	1	Miel de Abejas	Miel multifloral frasco 500g, Apiario El Cedro Palestina	18500.00	2026-05-24 12:51:59.605526
5	1	Cacao en Grano Seco	Cacao fermentado 6 días, secado solar, origen Macizo Colombiano	14200.00	2026-05-24 12:51:59.605526
6	1	cafe quindio	cafe aromatico	23.00	2026-05-24 15:58:33.154656
7	1	cafe caqueta	nuevo cafe saborizado	25.00	2026-05-24 16:03:06.830539
\.


--
-- TOC entry 5076 (class 0 OID 41396)
-- Dependencies: 220
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, nombre, email, password, created_at) FROM stdin;
1	Santiago Chavarro	schavarro@unbosque.edu.co	hashed_pass_1	2026-05-24 12:51:59.605526
2	Juan Pablo Sánchez	jpasanchez@unbosque.edu.co	hashed_pass_2	2026-05-24 12:51:59.605526
\.


--
-- TOC entry 5084 (class 0 OID 41463)
-- Dependencies: 228
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.venta (id, cliente_id, fecha, total, estado) FROM stdin;
1	1	2025-01-20 10:15:00	6000000.00	completada
2	2	2025-02-05 09:30:00	394000.00	completada
3	3	2025-03-12 11:00:00	225000.00	pendiente
\.


--
-- TOC entry 5098 (class 0 OID 0)
-- Dependencies: 221
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_seq', 3, true);


--
-- TOC entry 5099 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_venta_id_seq', 10, true);


--
-- TOC entry 5100 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventario_id_seq', 7, true);


--
-- TOC entry 5101 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_id_seq', 7, true);


--
-- TOC entry 5102 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 2, true);


--
-- TOC entry 5103 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.venta_id_seq', 3, true);


--
-- TOC entry 4908 (class 2606 OID 41420)
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- TOC entry 4918 (class 2606 OID 41492)
-- Name: detalle_venta detalle_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_pkey PRIMARY KEY (id);


--
-- TOC entry 4912 (class 2606 OID 41454)
-- Name: inventario inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_pkey PRIMARY KEY (id);


--
-- TOC entry 4914 (class 2606 OID 41456)
-- Name: inventario inventario_producto_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_producto_id_key UNIQUE (producto_id);


--
-- TOC entry 4910 (class 2606 OID 41435)
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id);


--
-- TOC entry 4904 (class 2606 OID 41410)
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- TOC entry 4906 (class 2606 OID 41408)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 4916 (class 2606 OID 41474)
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id);


--
-- TOC entry 4924 (class 2620 OID 41510)
-- Name: inventario trg_alerta_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_alerta_stock AFTER UPDATE ON public.inventario FOR EACH ROW EXECUTE FUNCTION public.fn_alerta_stock();


--
-- TOC entry 4926 (class 2620 OID 41506)
-- Name: detalle_venta trg_descontar_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_descontar_stock AFTER INSERT ON public.detalle_venta FOR EACH ROW EXECUTE FUNCTION public.fn_descontar_stock();


--
-- TOC entry 4925 (class 2620 OID 41504)
-- Name: inventario trg_inventario_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_inventario_updated BEFORE UPDATE ON public.inventario FOR EACH ROW EXECUTE FUNCTION public.fn_inventario_updated();


--
-- TOC entry 4927 (class 2620 OID 41508)
-- Name: detalle_venta trg_recalcular_total; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_recalcular_total AFTER INSERT OR DELETE OR UPDATE ON public.detalle_venta FOR EACH ROW EXECUTE FUNCTION public.fn_recalcular_total();


--
-- TOC entry 4922 (class 2606 OID 41498)
-- Name: detalle_venta detalle_venta_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.producto(id) ON DELETE RESTRICT;


--
-- TOC entry 4923 (class 2606 OID 41493)
-- Name: detalle_venta detalle_venta_venta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_venta_id_fkey FOREIGN KEY (venta_id) REFERENCES public.venta(id) ON DELETE CASCADE;


--
-- TOC entry 4920 (class 2606 OID 41457)
-- Name: inventario inventario_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.producto(id) ON DELETE CASCADE;


--
-- TOC entry 4919 (class 2606 OID 41436)
-- Name: producto producto_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE RESTRICT;


--
-- TOC entry 4921 (class 2606 OID 41475)
-- Name: venta venta_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.cliente(id) ON DELETE RESTRICT;


-- Completed on 2026-05-24 17:25:50

--
-- PostgreSQL database dump complete
--

\unrestrict w0AhKHIGjPJ2iOHsG9euHqBAyRsxedAnyUSrTqGKtukPhIFSVUawDQGTcgLgEfJ

