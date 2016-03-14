CREATE TABLE morphology
(
  id serial NOT NULL,
  features character varying,
  tagset_brown character varying,
  tagset_claws character varying,
  tagset_penn character varying,
  tagset_universal character varying,
  CONSTRAINT morphology_pkey PRIMARY KEY (id)
);

CREATE TABLE syntax
(
  id serial NOT NULL,
  features character varying,
  CONSTRAINT syntax_pkey PRIMARY KEY (id)
);

CREATE TABLE document
(
  id serial NOT NULL,
  scanned timestamp with time zone default now(),
  hash character varying,
  path character varying,
  date_created character varying,
  title character varying,
  authors character varying,
  tokenizer character varying,
  tagger character varying,
  lemmatizer character varying,
  stemmer character varying,
  syntaxer character varying,
  type character varying(20),
  CONSTRAINT document_pkey PRIMARY KEY (id)
);

CREATE TABLE corpus
(
  id serial NOT NULL,
  name character varying NOT NULL,
  CONSTRAINT corpus_pkey PRIMARY KEY (id)
);

CREATE TABLE membership
(
  doc_id integer NOT NULL,
  corpus_id integer NOT NULL,
  CONSTRAINT membership_doc_fkey FOREIGN KEY (doc_id) REFERENCES document (id) ON DELETE CASCADE,
  CONSTRAINT membership_corpus_fkey FOREIGN KEY (corpus_id) REFERENCES corpus (id) ON DELETE CASCADE
);

CREATE TABLE jot
(
    token character varying,
    lemma character varying,
    stem character varying,
    pos character(5),
    morph_id integer,
    syntax_id integer,
    doc_id integer,
	count integer,
    CONSTRAINT jot_doc_fkey FOREIGN KEY (doc_id) REFERENCES document (id) ON DELETE CASCADE
);

CREATE TABLE tally
(
    corpus_id integer NOT NULL,
    token character varying,
    lemma character varying,
    stem character varying,
    pos character(5),
    morph_id integer,
    syntax_id integer,
    doc_count integer,
    count integer,
    CONSTRAINT tally_corpus_fkey FOREIGN KEY (corpus_id) REFERENCES corpus (id) ON DELETE CASCADE  
);

CREATE TABLE batch
(
  id serial NOT NULL,
  action character varying NOT NULL,
  item character varying NOT NULL,
  options json,
  last_attempted timestamp with time zone,
  error character varying,
  CONSTRAINT batch_pkey PRIMARY KEY (id),
  CONSTRAINT batch_action_item_key UNIQUE (action, item)
);

CREATE INDEX membership_corpus_idx ON membership USING btree (corpus_id);

CREATE INDEX membership_doc_idx ON membership USING btree (doc_id);

CREATE INDEX jot_token_idx ON jot USING btree (token);

CREATE INDEX jot_lemma_idx ON jot USING btree (lemma);

CREATE INDEX jot_doc_idx ON jot USING btree (doc_id);

CREATE INDEX tally_corpus_idx ON tally USING btree (corpus_id);

CREATE INDEX tally_token_idx ON tally USING btree (token);

CREATE INDEX tally_lemma_idx ON tally USING btree (lemma);

CREATE TABLE delta
(
    lemma character varying,
	count integer
);

CREATE INDEX delta_lemma_idx ON delta USING btree (lemma);

CREATE TABLE dockw
(
    lemma character varying,
    doc_id integer,
	tfidf double precision,
    CONSTRAINT dockw_doc_fkey FOREIGN KEY (doc_id) REFERENCES document (id) ON DELETE CASCADE
);

CREATE INDEX dockw_lemma_idx ON delta USING btree (lemma);
