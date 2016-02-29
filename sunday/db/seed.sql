truncate patent cascade;

copy patent
(
  id,
  type,
  number,
  date,
  kind,
  abstract,
  title
)
from '/docker-entrypoint-initdb.d/seed/seed-patent.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy application
(
  id,
  patent_id,
  series_code,
  number,
  country,
  date
)
from '/docker-entrypoint-initdb.d/seed/seed-application.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy claim
( 
  uuid,
  patent_id,
  text,
  dependent,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-claim.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	', NULL 'NULL');

copy cpc_current
( 
  uuid,
  patent_id,
  section_id,
  subsection_id,
  group_id,
  subgroup_id,
  category,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-cpc-current.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy rawassignee
( 
  uuid,
  patent_id,
  assignee_id,
  rawlocation_id,
  type,
  name_first,
  name_last,
  organization,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-rawassignee.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy rawinventor
( 
  uuid,
  patent_id,
  inventor_id,
  rawlocation_id,
  name_first,
  name_last,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-rawinventor.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy rawlawyer
( 
  uuid,
  lawyer_id,
  patent_id,
  name_first,
  name_last,
  organization,
  country,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-rawlawyer.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy uspc_current
( 
  uuid,
  patent_id,
  mainclass_id,
  subclass_id,
  sequence
)
from '/docker-entrypoint-initdb.d/seed/seed-uspc-current.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');
