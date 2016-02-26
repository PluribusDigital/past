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
from 'C:/dvp/past/sunday/db/seed/seed-patent.txt'
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
from 'C:/dvp/past/sunday/db/seed/seed-application.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy claim
( 
  uuid,
  patent_id,
  text,
  dependent,
  sequence
)
from 'C:/dvp/past/sunday/db/seed/seed-claim.txt'
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
from 'C:/dvp/past/sunday/db/seed/seed-cpc-current.txt'
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
from 'C:/dvp/past/sunday/db/seed/seed-rawassignee.txt'
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
from 'C:/dvp/past/sunday/db/seed/seed-rawinventor.txt'
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
from 'C:/dvp/past/sunday/db/seed/seed-rawlawyer.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

copy uspc_current
( 
  uuid,
  patent_id,
  mainclass_id,
  subclass_id,
  sequence
)
from 'C:/dvp/past/sunday/db/seed/seed-uspc-current.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');
