TRUNCATE morphology RESTART IDENTITY;
TRUNCATE syntax RESTART IDENTITY;
TRUNCATE corpus RESTART IDENTITY CASCADE;
TRUNCATE document RESTART IDENTITY CASCADE;
TRUNCATE tally;
TRUNCATE batch;

COPY morphology
FROM '/docker-entrypoint-initdb.d/seed/seed-morphology.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY syntax
FROM '/docker-entrypoint-initdb.d/seed/seed-syntax.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY document
FROM '/docker-entrypoint-initdb.d/seed/seed-document.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY corpus
FROM '/docker-entrypoint-initdb.d/seed/seed-corpus.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY membership
FROM '/docker-entrypoint-initdb.d/seed/seed-membership.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY jot
FROM '/docker-entrypoint-initdb.d/seed/seed-jot.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

COPY tally
FROM '/docker-entrypoint-initdb.d/seed/seed-tally.txt'
WITH (FORMAT 'csv', HEADER true, DELIMITER '	');

--COPY batch
--FROM '/docker-entrypoint-initdb.d/seed/seed-batch.txt'
--WITH (FORMAT 'csv', HEADER true, DELIMITER '	');
