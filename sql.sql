-- Table: public.song

-- DROP TABLE public.song;

CREATE TABLE public.song
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 1000000 CACHE 1 ),
    songid character varying(255) COLLATE pg_catalog."default" NOT NULL,
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    performer character varying(255) COLLATE pg_catalog."default" NOT NULL,
    top_position integer,
    instnce integer,
    weeksonchart integer,
    CONSTRAINT song_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

-- Index: Name_index

-- DROP INDEX public."Name_index";

CREATE INDEX "Name_index"
    ON public.song USING btree
    (name COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: perfor_index

-- DROP INDEX public.perfor_index;

CREATE INDEX perfor_index
    ON public.song USING btree
    (performer COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: songid_index

-- DROP INDEX public.songid_index;

CREATE INDEX songid_index
    ON public.song USING btree
    (songid COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Table: public.weekly

-- DROP TABLE public.weekly;

CREATE TABLE public.weekly
(
    id bigint NOT NULL,
    weekid integer NOT NULL,
    url character varying(255) COLLATE pg_catalog."default" NOT NULL,
    pos integer NOT NULL,
    top_pos_wk integer NOT NULL
)

TABLESPACE pg_default;

-- Index: id_index

-- DROP INDEX public.id_index;

CREATE INDEX id_index
    ON public.weekly USING btree
    (id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table: public.weeks

-- DROP TABLE public.weeks;

CREATE TABLE public.weeks
(
    id bigint NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 10000 CACHE 1 ),
    weekinfo character varying(255) COLLATE pg_catalog."default" NOT NULL,
	weekdate date,
	year int,
    CONSTRAINT weeks_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

