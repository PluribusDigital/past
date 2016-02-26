-- drop table patent cascade;

CREATE TABLE patent
(
  id varchar(20) NOT NULL,
  type varchar(20) NOT NULL,
  number varchar(64) NOT NULL,
  date date,
  kind varchar(10),
  abstract text,
  title text,
  CONSTRAINT patent_pkey PRIMARY KEY (id)
);

CREATE TABLE application
(
  id varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  series_code varchar(20), 
  number varchar(64),
  country varchar(20),
  date date,
  CONSTRAINT application_pkey PRIMARY KEY (id),
  CONSTRAINT application_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE claim
( 
  uuid varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  text text, 
  dependent int, 
  sequence int,
  CONSTRAINT claim_pkey PRIMARY KEY (uuid),
  CONSTRAINT claim_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE cpc_current
( 
  uuid varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  section_id varchar (10), 
  subsection_id varchar(20),
  group_id varchar(20),
  subgroup_id varchar(20),
  category varchar(20), 
  sequence int,
  CONSTRAINT cpc_current_pkey PRIMARY KEY (uuid),
  CONSTRAINT cpc_current_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE rawassignee
( 
  uuid varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  assignee_id varchar(36), 
  rawlocation_id varchar(256), 
  type varchar (10), 
  name_first varchar(64), 
  name_last varchar(64), 
  organization varchar(128), 
  sequence int,
  CONSTRAINT rawassignee_pkey PRIMARY KEY (uuid),
  CONSTRAINT rawassignee_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE rawinventor
( 
  uuid varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  inventor_id varchar(36), 
  rawlocation_id varchar(256), 
  name_first varchar(64), 
  name_last varchar(64), 
  sequence int,
  CONSTRAINT rawinventor_pkey PRIMARY KEY (uuid),
  CONSTRAINT rawinventor_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE rawlawyer
( 
  uuid varchar(36) NOT NULL, 
  lawyer_id varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  name_first varchar(64), 
  name_last varchar(64), 
  organization varchar(64), 
  country varchar(10), 
  sequence int,
  CONSTRAINT rawlawyer_pkey PRIMARY KEY (uuid),
  CONSTRAINT rawlawyer_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);

CREATE TABLE uspc_current
( 
  uuid varchar(36) NOT NULL, 
  patent_id varchar(20) NOT NULL, 
  mainclass_id varchar(10),
  subclass_id varchar(20), 
  sequence int,
  CONSTRAINT uspc_current_pkey PRIMARY KEY (uuid),
  CONSTRAINT uspc_current_patent_fkey FOREIGN KEY (patent_id) REFERENCES patent (id) ON DELETE CASCADE
);


