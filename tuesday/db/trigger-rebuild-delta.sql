TRUNCATE delta;

INSERT INTO delta
SELECT source.lemma, sum(source.docs) as docs
FROM (
	SELECT lemma, count(DISTINCT doc_id) as docs
	FROM jot
	GROUP BY lemma
	UNION
	SELECT lemma, sum(doc_count) as docs
	FROM tally 
	GROUP BY lemma) as source
GROUP BY source.lemma;