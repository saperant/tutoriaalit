-- NULL ja kolmiarvoinen logiikka.
.headers on
.mode box
.nullvalue NULL

-- @alku vertailut
SELECT NULL = NULL          AS yhtasuuri,
       NULL <> 1            AS erisuuri,
       NULL IS NULL         AS is_null,
       NULL AND 0           AS ja_epatosi,
       NULL OR 1            AS tai_tosi,
       coalesce(NULL, 'oletus') AS coalesce;
-- @loppu vertailut
