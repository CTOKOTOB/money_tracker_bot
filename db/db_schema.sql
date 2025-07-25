--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Ubuntu 17.5-0ubuntu0.25.04.1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-0ubuntu0.25.04.1)

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
-- Name: app; Type: SCHEMA; Schema: -; Owner: moneybot
--

CREATE SCHEMA app;


ALTER SCHEMA app OWNER TO moneybot;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: benefits; Type: TABLE; Schema: app; Owner: moneybot
--

CREATE TABLE app.benefits (
    id integer NOT NULL,
    user_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT now()
);


ALTER TABLE app.benefits OWNER TO moneybot;

--
-- Name: benefits_id_seq; Type: SEQUENCE; Schema: app; Owner: moneybot
--

CREATE SEQUENCE app.benefits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.benefits_id_seq OWNER TO moneybot;

--
-- Name: benefits_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: moneybot
--

ALTER SEQUENCE app.benefits_id_seq OWNED BY app.benefits.id;


--
-- Name: categories; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.categories (
    id integer NOT NULL,
    user_id integer,
    name text NOT NULL
);


ALTER TABLE app.categories OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.categories_id_seq OWNER TO postgres;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: postgres
--

ALTER SEQUENCE app.categories_id_seq OWNED BY app.categories.id;


--
-- Name: expenses; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.expenses (
    id integer NOT NULL,
    user_id integer,
    category_id integer,
    amount numeric(10,2) NOT NULL,
    description text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.expenses OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.expenses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.expenses_id_seq OWNER TO postgres;

--
-- Name: expenses_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: postgres
--

ALTER SEQUENCE app.expenses_id_seq OWNED BY app.expenses.id;


--
-- Name: users; Type: TABLE; Schema: app; Owner: postgres
--

CREATE TABLE app.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    name text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE app.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: app; Owner: postgres
--

CREATE SEQUENCE app.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE app.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: postgres
--

ALTER SEQUENCE app.users_id_seq OWNED BY app.users.id;


--
-- Name: benefits id; Type: DEFAULT; Schema: app; Owner: moneybot
--

ALTER TABLE ONLY app.benefits ALTER COLUMN id SET DEFAULT nextval('app.benefits_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.categories ALTER COLUMN id SET DEFAULT nextval('app.categories_id_seq'::regclass);


--
-- Name: expenses id; Type: DEFAULT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.expenses ALTER COLUMN id SET DEFAULT nextval('app.expenses_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.users ALTER COLUMN id SET DEFAULT nextval('app.users_id_seq'::regclass);


--
-- Name: benefits benefits_pkey; Type: CONSTRAINT; Schema: app; Owner: moneybot
--

ALTER TABLE ONLY app.benefits
    ADD CONSTRAINT benefits_pkey PRIMARY KEY (id);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: expenses expenses_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.expenses
    ADD CONSTRAINT expenses_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: benefits benefits_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: moneybot
--

ALTER TABLE ONLY app.benefits
    ADD CONSTRAINT benefits_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE CASCADE;


--
-- Name: categories categories_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.categories
    ADD CONSTRAINT categories_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE CASCADE;


--
-- Name: expenses expenses_category_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.expenses
    ADD CONSTRAINT expenses_category_id_fkey FOREIGN KEY (category_id) REFERENCES app.categories(id);


--
-- Name: expenses expenses_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: postgres
--

ALTER TABLE ONLY app.expenses
    ADD CONSTRAINT expenses_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE CASCADE;


--
-- Name: TABLE categories; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON TABLE app.categories TO moneybot;


--
-- Name: SEQUENCE categories_id_seq; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON SEQUENCE app.categories_id_seq TO moneybot;


--
-- Name: TABLE expenses; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON TABLE app.expenses TO moneybot;


--
-- Name: SEQUENCE expenses_id_seq; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON SEQUENCE app.expenses_id_seq TO moneybot;


--
-- Name: TABLE users; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON TABLE app.users TO moneybot;


--
-- Name: SEQUENCE users_id_seq; Type: ACL; Schema: app; Owner: postgres
--

GRANT ALL ON SEQUENCE app.users_id_seq TO moneybot;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: app; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA app GRANT ALL ON SEQUENCES TO moneybot;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: app; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA app GRANT ALL ON TABLES TO moneybot;


--
-- PostgreSQL database dump complete
--

