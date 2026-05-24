--
-- PostgreSQL database dump
--

\restrict 4w3DS1YYJW6HBZLYEHrNWgyv5fnE3hS8CapOLohrgc216pQpUVc2DFtY7QKKda0

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-05-11 17:09:45

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
-- TOC entry 237 (class 1255 OID 33200)
-- Name: fn_alerta_stock(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_alerta_stock() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.cantidad <= NEW.cantidad_minima THEN
        RAISE NOTICE
            'ALERTA STOCK BAJO - Producto id=%, actual=%, minimo=%',
            NEW.producto_id, NEW.cantidad, NEW.cantidad_minima;
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.fn_alerta_stock() OWNER TO postgres;

--
-- TOC entry 235 (class 1255 OID 33196)
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
        RAISE EXCEPTION
            'Stock insuficiente. Producto id=%, stock actual=%, pedido=%',
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
-- TOC entry 234 (class 1255 OID 33194)
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
-- TOC entry 236 (class 1255 OID 33198)
-- Name: fn_recalcular_total(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.fn_recalcular_total() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_id INT;
BEGIN
    v_id := COALESCE(NEW.venta_id, OLD.venta_id);
    UPDATE venta
    SET total = (
        SELECT COALESCE(SUM(cantidad * precio_unitario), 0)
        FROM detalle_venta
        WHERE venta_id = v_id
    )
    WHERE id = v_id;
    RETURN COALESCE(NEW, OLD);
END;
$$;


ALTER FUNCTION public.fn_recalcular_total() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 32877)
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
-- TOC entry 221 (class 1259 OID 32876)
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
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 221
-- Name: cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_seq OWNED BY public.cliente.id;


--
-- TOC entry 230 (class 1259 OID 32952)
-- Name: detalle_venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_venta (
    id integer NOT NULL,
    venta_id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer NOT NULL,
    precio_unitario numeric(10,2) NOT NULL,
    CONSTRAINT detalle_venta_cantidad_check CHECK ((cantidad > 0)),
    CONSTRAINT detalle_venta_precio_unitario_check CHECK ((precio_unitario >= (0)::numeric))
);


ALTER TABLE public.detalle_venta OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 32951)
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
-- TOC entry 5119 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_venta_id_seq OWNED BY public.detalle_venta.id;


--
-- TOC entry 226 (class 1259 OID 32909)
-- Name: inventario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventario (
    id integer NOT NULL,
    producto_id integer NOT NULL,
    cantidad integer DEFAULT 0 NOT NULL,
    cantidad_minima integer DEFAULT 5 NOT NULL,
    updated_at timestamp without time zone DEFAULT now(),
    CONSTRAINT inventario_cantidad_check CHECK ((cantidad >= 0)),
    CONSTRAINT inventario_cantidad_minima_check CHECK ((cantidad_minima >= 0))
);


ALTER TABLE public.inventario OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 32908)
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
-- TOC entry 5120 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventario_id_seq OWNED BY public.inventario.id;


--
-- TOC entry 224 (class 1259 OID 32889)
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
-- TOC entry 223 (class 1259 OID 32888)
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
-- TOC entry 5121 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.producto_id_seq OWNED BY public.producto.id;


--
-- TOC entry 220 (class 1259 OID 32861)
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
-- TOC entry 219 (class 1259 OID 32860)
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
-- TOC entry 5122 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuario_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuario_id_seq OWNED BY public.usuario.id;


--
-- TOC entry 231 (class 1259 OID 32985)
-- Name: v_inventario; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_inventario AS
 SELECT p.id,
    p.nombre,
    p.precio,
    i.cantidad,
    i.cantidad_minima,
        CASE
            WHEN (i.cantidad <= i.cantidad_minima) THEN 'STOCK BAJO'::text
            ELSE 'OK'::text
        END AS alerta,
    i.updated_at
   FROM (public.producto p
     JOIN public.inventario i ON ((i.producto_id = p.id)));


ALTER VIEW public.v_inventario OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 32994)
-- Name: v_top_productos; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_top_productos AS
 SELECT p.nombre,
    sum(dv.cantidad) AS unidades_vendidas,
    sum(((dv.cantidad)::numeric * dv.precio_unitario)) AS ingresos_totales
   FROM (public.detalle_venta dv
     JOIN public.producto p ON ((p.id = dv.producto_id)))
  GROUP BY p.nombre
  ORDER BY (sum(dv.cantidad)) DESC;


ALTER VIEW public.v_top_productos OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 32934)
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
-- TOC entry 232 (class 1259 OID 32989)
-- Name: v_ventas_detalle; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.v_ventas_detalle AS
 SELECT v.id AS venta_id,
    v.fecha,
    v.estado,
    c.nombre AS cliente,
    p.nombre AS producto,
    dv.cantidad,
    dv.precio_unitario,
    ((dv.cantidad)::numeric * dv.precio_unitario) AS subtotal,
    v.total
   FROM (((public.venta v
     JOIN public.cliente c ON ((c.id = v.cliente_id)))
     JOIN public.detalle_venta dv ON ((dv.venta_id = v.id)))
     JOIN public.producto p ON ((p.id = dv.producto_id)));


ALTER VIEW public.v_ventas_detalle OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 32933)
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
-- TOC entry 5123 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.venta_id_seq OWNED BY public.venta.id;


--
-- TOC entry 4899 (class 2604 OID 32880)
-- Name: cliente id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id SET DEFAULT nextval('public.cliente_id_seq'::regclass);


--
-- TOC entry 4911 (class 2604 OID 32955)
-- Name: detalle_venta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta ALTER COLUMN id SET DEFAULT nextval('public.detalle_venta_id_seq'::regclass);


--
-- TOC entry 4903 (class 2604 OID 32912)
-- Name: inventario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario ALTER COLUMN id SET DEFAULT nextval('public.inventario_id_seq'::regclass);


--
-- TOC entry 4901 (class 2604 OID 32892)
-- Name: producto id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto ALTER COLUMN id SET DEFAULT nextval('public.producto_id_seq'::regclass);


--
-- TOC entry 4897 (class 2604 OID 32864)
-- Name: usuario id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id SET DEFAULT nextval('public.usuario_id_seq'::regclass);


--
-- TOC entry 4907 (class 2604 OID 32937)
-- Name: venta id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta ALTER COLUMN id SET DEFAULT nextval('public.venta_id_seq'::regclass);


--
-- TOC entry 5104 (class 0 OID 32877)
-- Dependencies: 222
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cliente (id, nombre, email, telefono, created_at) FROM stdin;
1	Juan Perez	juan.perez@email.com	3001234567	2026-05-11 16:33:23.8865
2	Maria Garcia	maria.garcia@email.com	3109876543	2026-05-11 16:33:23.8865
3	Carlos Lopez	carlos.lopez@email.com	3205551234	2026-05-11 16:33:23.8865
4	Ana Martinez	ana.martinez@email.com	3158887766	2026-05-11 16:33:23.8865
5	Pedro Rodriguez	pedro.rod@email.com	3004443322	2026-05-11 16:33:23.8865
\.


--
-- TOC entry 5112 (class 0 OID 32952)
-- Dependencies: 230
-- Data for Name: detalle_venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_venta (id, venta_id, producto_id, cantidad, precio_unitario) FROM stdin;
1	1	1	5	4500.00
2	1	2	10	1200.00
3	2	3	2	18000.00
4	2	4	3	3200.00
5	3	5	4	2800.00
6	4	6	2	5500.00
7	4	1	3	4500.00
\.


--
-- TOC entry 5108 (class 0 OID 32909)
-- Dependencies: 226
-- Data for Name: inventario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.inventario (id, producto_id, cantidad, cantidad_minima, updated_at) FROM stdin;
1	1	150	20	2026-05-11 16:33:23.8865
2	2	300	50	2026-05-11 16:33:23.8865
3	3	80	10	2026-05-11 16:33:23.8865
4	4	120	15	2026-05-11 16:33:23.8865
5	5	60	10	2026-05-11 16:33:23.8865
6	6	45	8	2026-05-11 16:33:23.8865
\.


--
-- TOC entry 5106 (class 0 OID 32889)
-- Dependencies: 224
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto (id, usuario_id, nombre, descripcion, precio, created_at) FROM stdin;
1	1	Cuaderno Universitario	Cuaderno 100 hojas rayado	4500.00	2026-05-11 16:33:23.8865
2	1	Esfero Azul	Esfero punta fina color azul	1200.00	2026-05-11 16:33:23.8865
3	2	Resma de Papel	Papel carta 500 hojas 75gr	18000.00	2026-05-11 16:33:23.8865
4	2	Carpeta Plastica	Carpeta con gancho plastico	3200.00	2026-05-11 16:33:23.8865
5	3	Marcador Tablero	Marcador borrable negro	2800.00	2026-05-11 16:33:23.8865
6	3	Tijeras Metalicas	Tijeras 18cm punta roma	5500.00	2026-05-11 16:33:23.8865
\.


--
-- TOC entry 5102 (class 0 OID 32861)
-- Dependencies: 220
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuario (id, nombre, email, password, created_at) FROM stdin;
1	Admin Sistema	admin@inventario.com	hash_admin_123	2026-05-11 16:33:23.8865
2	Santiago Chavarro	santiago@inventario.com	hash_santiago_456	2026-05-11 16:33:23.8865
3	Juan Pablo	juanpablo@inventario.com	hash_juan_789	2026-05-11 16:33:23.8865
4	Supervisor	supervisor@inventario.com	hash_super_000	2026-05-11 16:33:23.8865
\.


--
-- TOC entry 5110 (class 0 OID 32934)
-- Dependencies: 228
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.venta (id, cliente_id, fecha, total, estado) FROM stdin;
1	1	2026-05-11 16:33:23.8865	0.00	completada
2	2	2026-05-11 16:33:23.8865	0.00	completada
3	3	2026-05-11 16:33:23.8865	0.00	pendiente
4	4	2026-05-11 16:33:23.8865	0.00	completada
5	5	2026-05-11 16:33:23.8865	0.00	cancelada
\.


--
-- TOC entry 5124 (class 0 OID 0)
-- Dependencies: 221
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_seq', 5, true);


--
-- TOC entry 5125 (class 0 OID 0)
-- Dependencies: 229
-- Name: detalle_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_venta_id_seq', 7, true);


--
-- TOC entry 5126 (class 0 OID 0)
-- Dependencies: 225
-- Name: inventario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventario_id_seq', 6, true);


--
-- TOC entry 5127 (class 0 OID 0)
-- Dependencies: 223
-- Name: producto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.producto_id_seq', 6, true);


--
-- TOC entry 5128 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 4, true);


--
-- TOC entry 5129 (class 0 OID 0)
-- Dependencies: 227
-- Name: venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.venta_id_seq', 5, true);


--
-- TOC entry 4923 (class 2606 OID 32887)
-- Name: cliente cliente_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_email_key UNIQUE (email);


--
-- TOC entry 4925 (class 2606 OID 32885)
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- TOC entry 4939 (class 2606 OID 32964)
-- Name: detalle_venta detalle_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_pkey PRIMARY KEY (id);


--
-- TOC entry 4931 (class 2606 OID 32923)
-- Name: inventario inventario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_pkey PRIMARY KEY (id);


--
-- TOC entry 4933 (class 2606 OID 32925)
-- Name: inventario inventario_producto_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_producto_id_key UNIQUE (producto_id);


--
-- TOC entry 4928 (class 2606 OID 32902)
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id);


--
-- TOC entry 4919 (class 2606 OID 32875)
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- TOC entry 4921 (class 2606 OID 32873)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 4937 (class 2606 OID 32945)
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id);


--
-- TOC entry 4940 (class 1259 OID 32984)
-- Name: idx_detalle_producto; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_detalle_producto ON public.detalle_venta USING btree (producto_id);


--
-- TOC entry 4941 (class 1259 OID 32983)
-- Name: idx_detalle_venta; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_detalle_venta ON public.detalle_venta USING btree (venta_id);


--
-- TOC entry 4929 (class 1259 OID 32980)
-- Name: idx_inventario_prod; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_inventario_prod ON public.inventario USING btree (producto_id);


--
-- TOC entry 4926 (class 1259 OID 32979)
-- Name: idx_producto_usuario; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_producto_usuario ON public.producto USING btree (usuario_id);


--
-- TOC entry 4934 (class 1259 OID 32981)
-- Name: idx_venta_cliente; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_venta_cliente ON public.venta USING btree (cliente_id);


--
-- TOC entry 4935 (class 1259 OID 32982)
-- Name: idx_venta_fecha; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_venta_fecha ON public.venta USING btree (fecha);


--
-- TOC entry 4947 (class 2620 OID 33201)
-- Name: inventario trg_alerta_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_alerta_stock AFTER UPDATE ON public.inventario FOR EACH ROW EXECUTE FUNCTION public.fn_alerta_stock();


--
-- TOC entry 4949 (class 2620 OID 33197)
-- Name: detalle_venta trg_descontar_stock; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_descontar_stock AFTER INSERT ON public.detalle_venta FOR EACH ROW EXECUTE FUNCTION public.fn_descontar_stock();


--
-- TOC entry 4948 (class 2620 OID 33195)
-- Name: inventario trg_inventario_updated; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_inventario_updated BEFORE UPDATE ON public.inventario FOR EACH ROW EXECUTE FUNCTION public.fn_inventario_updated();


--
-- TOC entry 4950 (class 2620 OID 33199)
-- Name: detalle_venta trg_recalcular_total; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trg_recalcular_total AFTER INSERT OR DELETE OR UPDATE ON public.detalle_venta FOR EACH ROW EXECUTE FUNCTION public.fn_recalcular_total();


--
-- TOC entry 4945 (class 2606 OID 32970)
-- Name: detalle_venta detalle_venta_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.producto(id) ON DELETE RESTRICT;


--
-- TOC entry 4946 (class 2606 OID 32965)
-- Name: detalle_venta detalle_venta_venta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_venta_id_fkey FOREIGN KEY (venta_id) REFERENCES public.venta(id) ON DELETE CASCADE;


--
-- TOC entry 4943 (class 2606 OID 32926)
-- Name: inventario inventario_producto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventario
    ADD CONSTRAINT inventario_producto_id_fkey FOREIGN KEY (producto_id) REFERENCES public.producto(id) ON DELETE CASCADE;


--
-- TOC entry 4942 (class 2606 OID 32903)
-- Name: producto producto_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuario(id) ON DELETE RESTRICT;


--
-- TOC entry 4944 (class 2606 OID 32946)
-- Name: venta venta_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.cliente(id) ON DELETE RESTRICT;


-- Completed on 2026-05-11 17:09:45

--
-- PostgreSQL database dump complete
--

\unrestrict 4w3DS1YYJW6HBZLYEHrNWgyv5fnE3hS8CapOLohrgc216pQpUVc2DFtY7QKKda0

