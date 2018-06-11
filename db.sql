--
-- PostgreSQL database dump
--

-- Dumped from database version 9.6.8
-- Dumped by pg_dump version 10.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: exhibitor; Type: TABLE; Schema: public; Owner: cantonfair
--

CREATE TABLE exhibitor (
    id integer NOT NULL,
    url character varying(2044) NOT NULL,
    is_done boolean DEFAULT false,
    company_name character varying(2044),
    address character varying(2044),
    city_province character varying(2044),
    post_code character varying(2044),
    website character varying(2044),
    main_products character varying(2044),
    international_commercial_terms character varying(2044),
    exhibition_records character varying(2044),
    number_of_staff character varying(2044),
    registered_capital character varying(2044),
    business_type character varying(2044),
    target_customer character varying(2044),
    category_name character varying(2044)
);


ALTER TABLE exhibitor OWNER TO cantonfair;

--
-- Name: exhibitors_id_seq; Type: SEQUENCE; Schema: public; Owner: cantonfair
--

CREATE SEQUENCE exhibitors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE exhibitors_id_seq OWNER TO cantonfair;

--
-- Name: exhibitors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cantonfair
--

ALTER SEQUENCE exhibitors_id_seq OWNED BY exhibitor.id;


--
-- Name: exhibitors_url_seq; Type: SEQUENCE; Schema: public; Owner: cantonfair
--

CREATE SEQUENCE exhibitors_url_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE exhibitors_url_seq OWNER TO cantonfair;

--
-- Name: exhibitors_url_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cantonfair
--

ALTER SEQUENCE exhibitors_url_seq OWNED BY exhibitor.url;


--
-- Name: exhibitor id; Type: DEFAULT; Schema: public; Owner: cantonfair
--

ALTER TABLE ONLY exhibitor ALTER COLUMN id SET DEFAULT nextval('exhibitors_id_seq'::regclass);


--
-- Name: exhibitor url; Type: DEFAULT; Schema: public; Owner: cantonfair
--

ALTER TABLE ONLY exhibitor ALTER COLUMN url SET DEFAULT nextval('exhibitors_url_seq'::regclass);


--
-- Name: exhibitor exhibitor_url_key; Type: CONSTRAINT; Schema: public; Owner: cantonfair
--

ALTER TABLE ONLY exhibitor
    ADD CONSTRAINT exhibitor_url_key UNIQUE (url);


--
-- Name: exhibitor exhibitors_pkey; Type: CONSTRAINT; Schema: public; Owner: cantonfair
--

ALTER TABLE ONLY exhibitor
    ADD CONSTRAINT exhibitors_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--
